from kspy import kspy

'''
(install_type,
    slot,
    host_name,
    host_ip,
    host_subnet,
    host_gw,
    host_dns)

'''

def main():
    kspy.main('install',
    '1',
    'sample-host01',
    '192.168.1.22',
    '255.255.255.0',
    '192.168.1.1',
    '192.168.1.53')


if __name__ == '__main__':
    main()

# future enhancements
# mount iso to server using XCC Redfish ASPI?
# Power on server
# wait for ping response
# add to vcenter (vCenter REST API OR PyVmOmi)
