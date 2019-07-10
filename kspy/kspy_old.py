import requests
# Import standard python modules.
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

from pycdlib import pycdlib


# Create a new PyCdlib object.
iso = pycdlib.PyCdlib()

# user defined parameters
esxi_hostname = "GPS-BL-VH-10"
esxi_ip = "192.168.10.10"
staging_slot = 2
install_type = "install"   # Upgrade, Install or InstallPreserve

# fixed parameters for esxi network
esxi_subnet = "255.255.255.0"
esxi_gateway = "192.168.10.1"
esxi_dns1 = "192.168.10.40"

# Get IMM credentials
'''
 $IMMCred = get-credential -Message "Enter the credentials to connect to the IMM"
'''
#Convert variables to lower case.
esxi_hostname.lower()
install_type.lower()


# Select Staging Slot ISO Image
if staging_slot == 1:
    iso_image = "E:\ISO\VMware-ESXi-6.7.1_S1.iso"
elif staging_slot == 2:
    iso_image = "E:\ISO\VMware-ESXi-6.7.1_S2.iso"
#else:
#    iso_image = "E:\ISO\xxxx_3"

# Set install type in answer file.
if install_type == "install":
    installation = '''
# clear partitions and install
clearpart --firstdisk --overwritevmfs      
install --firstdisk --overwritevmfs --novmfsondisk
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


#Create ESXi ks.cfg Configuration file
'''
 write-host "Creating ESXi install config file" -ForegroundColor Cyan
 '''

# Create Kickstart file - Creates array with content, then written to text
config = f'''
### Stage 01 - Pre Installation:

#Accept the VMware End User License Agreement
vmaccepteula

{installation}

# set the root password
rootpw --iscrypted $1$p7oK4WFL$6LHXJ0Fi7opDHdEU7KKw5/

keyboard 'United Kingdom'

# Host Network Settings  
network --bootproto=static --addvmportgroup=1 --ip={esxi_ip} --netmask={esxi_subnet} --gateway={esxi_gateway} --nameserver={esxi_dns1} --hostname={esxi_hostname}
reboot

### Stage 02 - Post Installation:

# Firstboot
%firstboot --interpreter=busybox
sleep 30

# Enter Maintenance mode
vim-cmd hostsvc/maintenance_mode_enter

#suppress Shell Warning
esxcli system settings advanced set -o /UserVars/SuppressShellWarning -i 1
esxcli system settings advanced set -o /UserVars/ESXiShellTimeOut -i 1


# Set Search Domain
esxcli network ip dns search add --domain=gps-bl-rm-ad01.local

# Add DNS Nameservers to /etc/resolv.conf
cat > /etc/resolv.conf << \DNS
nameserver {esxi_dns1}
DNS

# Add NTP Server addresses
echo "server 192.168.10.40" >> /etc/ntp.conf;

# Allow NTP through firewall
esxcfg-firewall -e ntpClient

# enable NTP autostart
/sbin/chkconfig ntpd on;

# Disable CEIP
esxcli system settings advanced set -o /UserVars/HostClientCEIPOptIn -i 2
    
# VSwitch & Portgroup Configuration
esxcli network vswitch standard add --vswitch-name=vSwitch0 --ports=24
esxcli network vswitch standard uplink add --uplink-name=vmnic0 --vswitch-name=vSwitch0
esxcli network vswitch standard uplink add --uplink-name=vmnic3 --vswitch-name=vSwitch0
esxcli network vswitch standard policy security set --allow-mac-change=false --allow-forged-transmits=false --allow-promiscuous=false --vswitch-name=vSwitch0 
esxcli network vswitch standard policy failover set --active-uplinks=vmnic0 --vswitch-name=vSwitch0

esxcli network vswitch standard portgroup policy failover set --portgroup-name="Management Network" --active-uplinks=vmnic0 --standby-uplinks=vmnic3
esxcli network vswitch standard portgroup set -p "Management Network" --vlan-id 10

esxcli network vswitch standard portgroup add --portgroup-name=vmk_vmotion --vswitch-name=vswitch0
esxcli network vswitch standard portgroup set -p vmk_vmotion --vlan-id 20

esxcli network vswitch standard portgroup remove --portgroup-name="VM Network" --vswitch-name=vSwitch0

# Reboot
sleep 30
reboot
'''


# Open up a file object.  This causes PyCdlib to parse all of the metadata on the
# ISO, which is used for later manipulation.
iso.open(iso_image)

ksstr = bytes(config, 'utf-8')

iso.modify_file_in_place(BytesIO(ksstr), len(ksstr), '/KS.CFG;1')

modifiediso = BytesIO()
iso.write_fp(modifiediso)
iso.close()