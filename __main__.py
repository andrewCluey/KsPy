from kspy import kspy

'''
(install_type,
    slot,
    host_name,
    host_ip,
    host_subnet,
    host_gw,
    host_dns,
    iso_directory
    )

'''

def main():
    kspy.main('install',
    '1',
    'sample-host01',
    '192.168.100.22',
    '255.255.255.0',
    '192.168.100.1',
    '192.168.100.53',
    'D:\ISO')


if __name__ == '__main__':
    main()

# future enhancements
# mount iso to server using XCC Redfish ASPI?
# Power on server
# wait for ping response
# add to vcenter (vCenter REST API OR PyVmOmi)
