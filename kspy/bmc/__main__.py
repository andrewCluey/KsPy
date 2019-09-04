import mount_iso as mount

'''
'ip': IP Address of the BMC to mount the ISo to

'login_account': BMC User name

'login_password': BMC Password

'fsprotocol': protocol to connect to the file server (HTTP or NFS)
'fsip': IP address of the file server
'fsport': Port to use for connecting to the file server
'image': File name of the media image to mount (eg vsphere_6.iso)
'fsdir': Directory on the file server where the image is stored
'inserted': Integer. Is image treated as 'inserted' when action complete. Default True(0 or 1). 
'writeprotocol': Integer. Remote media is to be write protected or not. 

'''

def main():
    mount.main('192.168.10.205','xca_user','-orwIpFNzu','NFS','192.168.10.40','','VMware-ESXi-6.7.1_S1.iso','/iso/','1','1')

if __name__ == '__main__':
    main()
