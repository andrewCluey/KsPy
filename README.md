# KsPy

Simple Python package that will accept user input (such as a proposed esxi password), creates a kickstart file that is then saved to a vSphere ISO image.
vSphere ISO image can then be mounted to a physical server for the unattended deployment to start.

The unnatended kickstart script (ks.cfg) currently configures the following settings on the vSphere host:

- Core VMKernel management settings to a local vSwitch (management IP, Mask, DNS, NTP etc).
- sets root password
- Places the host into maintenance mode at startup
- IPv6 is left enabled (see https://kb.vmware.com/s/article/2150794).
- See section on vSwitch configuration below

## vSwitch configuration

- Creates standard vSwitch for management (vSwitch0)
- Adds 2 uplinks to the vSwitch using vmnic0 & vmnic6 (this assumes a certain physical layout on the host server. Will need verification after install)
- Sets security policy to not allow Mac Address changes or forged transmits.
- Sets promiscuous mode to false
- Default failover policy to vmnic0 as active
- Configures management VMKernel failover policy to vmnic0 active, vmnic6 as standby.
- Configures vmkernel management portgroup with VLAN ID 10
- Creates vmkernel portgroup for vMotion.
- Sets vmkernel vMotion portgroup to VLAN ID 20
- removes the default Virtual Machine portgroup "VM Network"

## Future changes

- Make passing arguments easier with validated inputs (argparse/CLi/Menu etc)
- auto mount the ISO to a specified server (using redfish/BMC) and power on
- expand ks.cfg file to finalise more host config (hardening, users, AD etc)
- move ks.cfg to a separate template file of some sort
- error handling in functions

## Running KsPy

- Clone the KsPy repository (try to clone KsPy to a system with connectivity to the physical servers BMC)
- Edit the input parameters (see below) in the '__main__.py' file
- Run the following commend from your shell:

```shell
python KsPy
```

- You will be prompted to enter a password for the new esxi host

## parameters

The main() function in __main__.py  is where the input paramaters are edited, KsPy will then read these values when it is executed.

The required parameters are:
'''python
(install_type,
    slot,
    host_name,
    host_ip,
    host_subnet,
    host_gw,
    host_dns)

'''
Here's a practical example:

'''python
def main():
    kspy.main('install',
    '1',
    'sample-host01',
    '192.168.1.22',
    '255.255.255.0',
    '192.168.1.1',
    '192.168.1.53')
'''
Remember, the paramaters have to be added in this order for KsPy to execute correctly.

Most fo the paramaters are self-explanatory (IP address, host name etc), some require further explanation.

### install_type

There are 3 install types. Whatever is chosen defines how ESXi is inatlled and what happens to existing data on the host.
The 3 types are:

- install : clears existing partitions and performs a new installation of esxi
- upgrade :  Retains existing VMFS datastores and upgrades esxi
- installpreserve : Performs a new installation of esxi but retains existing VMFS datastores

### slot

Needs to be either '1' or '2'.
Currently, the slot parameter is used to define which base ISO image is used for the deployment. This simply means that 2 ESXi hostys can be deployed at once.

In future updates, the slot paramater will likely be used to enhance deployment options for physical servers.
