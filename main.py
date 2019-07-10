from kspy.kspy import kspy

# (install_type, slot, host_name, host_ip, host_subnet, host_gw, host_dns)

def main():
    kspy.main('install', 
    '1', 
    'test122', 
    '192.168.232.122', 
    '255.255.255.0', 
    '192.168.232.1', 
    '192.168.10.40')


if __name__ == '__main__':
    main()




# mount iso to server using XCC Redfish ASPI?

# Power on server

# wait for ping response

# add to vcenter (vCenter REST API OR PyVmOmi)
