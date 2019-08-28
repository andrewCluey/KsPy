# Import standard python modules.
import requests
import getpass
from passlib.hash import sha512_crypt
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

from kspy.pycdlib import pycdlib


def pw_crypt():
    ''' Function to hash an inputed string. Hashed string is then saved to variable and returned. '''
    pw = getpass.getpass(prompt='Enter the proposed esxi password: ')
    resp = sha512_crypt.hash(pw)
    return resp


def create_ks(
                install_type,
                esxi_hostname,
                esxi_ip,
                esxi_subnet,
                esxi_gateway,
                esxi_dns1,
                root_pw
            ):
    ''' Description: creates the kickstart config file based on user inputs.
        :type install_type: String
        :param install_type: Is this a new installation or upgrade?
		            'install' (existing partitions are removed).
		            'upgrade' - upgrades esxi, preserves VMFS datastores
		            'installpreserve' - New install but preserves any VMFS partitions found.
    
        :type esxi_hostname: String
        :param esxi_hostname: The hostname to be applied to the new server.
    
        :type esxi_ip: String
        :param esxi_ip: The management (VMkernel) IP address for the new server.
    
        :type esxi_subnet: String
        :param esxi_subnet: The subnet for the management interface.
    
        :type esxi_gateway: String
        :param esxi_gateway: The gateway for the management interface
    
        :type esxi_dns1: String
        :param esxi_dns1: The IP address of the primary DNS server.
    
        :raises:
    
        :rtype:'''
    if install_type == "install":
        installation = '''
# clear partitions and install
clearpart --firstdisk --overwritevmfs      
install --firstdisk --overwritevmfs
'''
    elif install_type == "upgrade":
        installation = '''
# Upgrade esxi installation - maintain password & preserve VMFS
upgrade --firstdisk --preservevmfs
'''
    elif install_type == "installpreserve":
        installation = '''
# New esxi installation - Preserve VMFS
install --firstdisk --preservevmfs
'''
    #Convert variables to lower case.
    esxi_hostname = esxi_hostname.lower()
    install_type = install_type.lower()


# Create Kickstart file - Creates array with content, then written to text
    mod_text = f'''
#Accept the VMware End User License Agreement
vmaccepteula

{installation}

# set the root password

rootpw --iscrypted {root_pw}

# Host Network Settings  
network --bootproto=static --addvmportgroup=1 --ip={esxi_ip} --netmask={esxi_subnet} --gateway={esxi_gateway} --nameserver={esxi_dns1} --hostname={esxi_hostname}
reboot

# Firstboot
%firstboot --interpreter=busybox
sleep 30

# Enter Maintenance mode
vim-cmd hostsvc/maintenance_mode_enter

#suppress Shell Warning
esxcli system settings advanced set -o /UserVars/SuppressShellWarning -i 1
esxcli system settings advanced set -o /UserVars/ESXiShellTimeOut -i 1

# Add DNS Nameservers to /etc/resolv.conf
cat > /etc/resolv.conf << \DNS
nameserver {esxi_dns1}
DNS

# Add NTP Server addresses
echo "server 192.168.10.40" >> /etc/ntp.conf;

# Allow NTP through firewall
esxcfg-firewall -e ntpClient

# Disable CEIP
esxcli system settings advanced set -o /UserVars/HostClientCEIPOptIn -i 2
    
# VSwitch & Portgroup Configuration
esxcli network vswitch standard add --vswitch-name=vSwitch0 --ports=24
esxcli network vswitch standard uplink add --uplink-name=vmnic0 --vswitch-name=vSwitch0
esxcli network vswitch standard uplink add --uplink-name=vmnic6 --vswitch-name=vSwitch0
esxcli network vswitch standard policy security set --allow-mac-change=false --allow-forged-transmits=false --allow-promiscuous=false --vswitch-name=vSwitch0 
esxcli network vswitch standard policy failover set --active-uplinks=vmnic0 --vswitch-name=vSwitch0

esxcli network vswitch standard portgroup policy failover set --portgroup-name="Management Network" --active-uplinks=vmnic0 --standby-uplinks=vmnic6
esxcli network vswitch standard portgroup set -p "Management Network" --vlan-id 10

esxcli network vswitch standard portgroup add --portgroup-name=vmk_vmotion --vswitch-name=vswitch0
esxcli network vswitch standard portgroup set -p vmk_vmotion --vlan-id 20

esxcli network vswitch standard portgroup remove --portgroup-name="VM Network" --vswitch-name=vSwitch0

# Reboot
sleep 30
reboot
'''
    return mod_text


def stage_slot(slo,iso_directory):
    ''' Description: Which staging slot (ISO Image) is to be used.
    :type slot: String. 
    :param slot: Must be either '1' or '2'

    :type iso_directory: String
    :param iso_directory: Directory where the ESXi image (ISO) is stored. Shoul dbe local directory. Example "D:\ISO"

    :raises:

    :rtype:
    '''
    if slot == '1':
        iso_image = f"{iso_directory}\VMware-ESXi-6.7.1_S1.iso"
    elif slot == '2':
        iso_image = f"{iso_directory}\VMware-ESXi-6.7.1_S2.iso"
    return iso_image

def iso_mod(
            iso_path,
            mod_text,
            iso_file
            ):
    ''' Opens up an ISO file object. Takes kickstart config text (mod_text), converts to utf-8
    and writes this to a new ISO file.    
    '''
    
    ksstr = bytes(mod_text, 'utf-8')
    iso = pycdlib.PyCdlib()
    iso.open(iso_path)

    iso.modify_file_in_place(BytesIO(ksstr), len(ksstr), '/' + iso_file + ';1')
    modifiediso = BytesIO()
    iso.write_fp(modifiediso)
    iso.close()


def main(install_type, 
            slot, 
            host_name, 
            host_ip, 
            host_subnet, 
            host_gw, 
            host_dns,
            iso_directory):
    """ Description
        :type install_type:
        :param install_type:
    
        :type slot:
        :param slot:
    
        :type host_name:
        :param host_name:
    
        :type host_ip:
        :param host_ip:
    
        :type host_subnet:
        :param host_subnet:
    
        :type host_gw:
        :param host_gw:
    
        :type host_dns:
        :param host_dns:

        :type iso_directory:
        :param iso_directory:
    
        :raises:
    
        :rtype:
    """
    path = stage_slot(slot,iso_directory)
    root_pw = pw_crypt()
    conf = create_ks(
                        install_type, 
                        host_name, 
                        host_ip, 
                        host_subnet, 
                        host_gw, 
                        host_dns, 
                        root_pw
                    )
    iso_mod(path, conf, 'KS.CFG')
