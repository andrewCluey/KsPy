import sys
import getpass
import json
import redfish
from kspy.bmc import lenovo_utils as utils


def _create_session(ip, login_account):
    '''Creates an authenticated session to the Redfish API'''
    login_password = getpass.getpass(prompt='Enter the IMM password: ')
    login_host = f"https://{ip}"
    # Connect using the address, account name, and password
        # Create a REDFISH object
    REDFISH_OBJ = redfish.redfish_client(
                                         base_url=login_host, 
                                         username=login_account,
                                         password=login_password, 
                                         default_prefix='/redfish/v1'
                                         )
    REDFISH_OBJ.login(auth="session")

def _mount_iso(
                ip, 
                login_account, 
                login_password, 
                fsprotocol, 
                fsip, 
                fsport, 
                image, 
                fsdir, 
                inserted, 
                writeprotocol
                ):
    """Mount an ISO or IMG image file from a file server to the host as a DVD or USB drive.
    :params ip: BMC IP address
    :type ip: string

    :params login_account: BMC user name
    :type login_account: string
    
    :params login_password: BMC user password
    :type login_password: string
    
    :params fsip:Specify the file server ip
    :type fsip:string
    
    :params fsdir:File path of the image
    :type fsdir:string
    
    :params image: file name of the image to mount
    :type image:string
    
    :params inserted:This value shall specify if the image is to be treated as inserted upon completion of the action. If this parameter is not provided by the client, the service shall default this value to be true.
    :type inserted: int
    
    :params writeProtected:This value shall specify if the remote media is supposed to be treated as write protected. If this parameter is not provided by the client, the service shall default this value to be true
    :type writeProtected: int
    
    :returns: returns mount media iso result when succeeded or error message when failed
    """
    result = {}
    login_host = f"https://{ip}"
    # Login into the server and create a session
    try:
        # Connect using the address, account name, and password
        # Create a REDFISH object
        REDFISH_OBJ = redfish.redfish_client(
                                            base_url=login_host, 
                                            username=login_account,
                                            password=login_password, 
                                            default_prefix='/redfish/v1'
                                            )
        REDFISH_OBJ.login(auth="session")
    except:
        result = {'ret': False, 'msg': "Please check the username, password, IP is correct\n"}
        return result

    try:
        # Get ServiceRoot resource
        response_base_url = REDFISH_OBJ.get('/redfish/v1', None)

        # Get Managers resource
        if response_base_url.status == 200:
            managers_url = response_base_url.dict['Managers']['@odata.id']
        else:
            error_message = utils.get_extended_error(response_base_url)
            result = {'ret': False, 'msg': " Url '/redfish/v1' response Error code %s \nerror_message: %s" % (
            response_base_url.status, error_message)}
            return result

        response_managers_url = REDFISH_OBJ.get(managers_url, None)
        if response_managers_url.status == 200:
            # Get manager url form manager resource instance
            count = response_managers_url.dict['Members@odata.count']
            for i in range(count):
                manager_url = response_managers_url.dict['Members'][i]['@odata.id']
                response_manager_url = REDFISH_OBJ.get(manager_url, None)
                if response_manager_url.status == 200:
                    # Get the virtual media url from the manger response
                    virtual_media_url = response_manager_url.dict['VirtualMedia']['@odata.id']
                else:
                    error_message = utils.get_extended_error(response_manager_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (
                        manager_url, response_manager_url.status, error_message)}
                    return result

                # Get the mount virtual media list
				# For the latest XCC Firmware(version is 2.5 and above), there are 10 predefined members
                response_virtual_media = REDFISH_OBJ.get(virtual_media_url, None)
                if response_virtual_media.status == 200:
                    members_list = response_virtual_media.dict["Members"]
                else:
                    error_message = utils.get_extended_error(response_virtual_media)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (
                        virtual_media_url, response_virtual_media.status, error_message)}
                    return result

                # Get the members url from the members list
                for members in members_list:
                    members_url = members["@odata.id"]
                    if members_url.split('/')[-1].startswith("EXT"):

                        # Get the mount image name from the members response resource
                        response_members = REDFISH_OBJ.get(members_url, None)
                        if response_members.status == 200:
                            image_name = response_members.dict["ImageName"]
                        else:
                            error_message = utils.get_extended_error(response_members)
                            result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (
                                members_url, response_members.status, error_message)}
                            return result

                        # Via patch request mount virtual media
                        port = (lambda fsport: ":" + fsport if fsport else fsport)
                        dir = (lambda fsdir: "/" + fsdir.strip("/") if fsdir else fsdir)
                        protocol = fsprotocol.lower()
                        fsport = port(fsport)
                        fsdir = dir(fsdir)
                        if image_name is None:
                            if protocol == "nfs":
                                image_uri = fsip + fsport + ":" + fsdir + "/" + image
                            else:
                                image_uri = protocol + "://" + fsip + fsport + fsdir + "/" + image
                            body = {"Image": image_uri, "WriteProtected": bool(writeprotocol),
                                    "Inserted": bool(inserted)}
                            response = REDFISH_OBJ.patch(members_url, body=body)
                            if response.status in [200, 204]:
                                result = {'ret': True, 'msg': "'%s' mount successfully" % image}
                                return result
                            else:
                                error_message = utils.get_extended_error(response)
                                result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (
                                    members_url, response.status, error_message)}
                                return result
                        else:
                            continue
                result = {'ret': False, 'msg': "Up to 4 files can be concurrently mounted to the server by the BMC."}
                return result
        else:
            error_message = utils.get_extended_error(response_managers_url)
            result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (
            managers_url, response_managers_url.status, error_message)}
    except Exception as e:
        result = {'ret': False, 'msg': "error_message: %s" % (e)}
    finally:
        # Logout of the current session
        REDFISH_OBJ.logout()
        return result


def _get_power_state(ip, login_account, system_id):
    """Get power state    
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :params system_id: ComputerSystem instance id(None: first instance, All: all instances)
    :type system_id: None or string
    :returns: returns power state when succeeded or error message when failed
    """
    login_password = getpass.getpass(prompt='Enter the IMM password: ')
    result = {}
    login_host = f"https://{ip}"
    try:
        # Connect using the BMC address, account name, and password
        # Create a REDFISH object
        REDFISH_OBJ = redfish.redfish_client(
                                            base_url=login_host, 
                                            username=login_account,
                                            password=login_password, 
                                            default_prefix='/redfish/v1'
                                            )
        # Login into the server and create a session
        REDFISH_OBJ.login(auth="session")
    except:
        result = {'ret': False, 'msg': 
                    "Please check the username, password, IP is correct"
                    }
        return result
    # GET the ComputerSystem resource
    power_details = []
    system = utils.get_system_url("/redfish/v1", system_id, REDFISH_OBJ)
    if not system:
        result = {'ret': False, 'msg': "This system id is not exist or system member is None"}
        REDFISH_OBJ.logout()
        return result
    for i in range(len(system)):
        system_url = system[i]
        response_system_url = REDFISH_OBJ.get(system_url, None)
        if response_system_url.status == 200:
            # Get the response
            power_state = {}
            # Get the PowerState property
            PowerState = response_system_url.dict["PowerState"]   # 
            power_state["PowerState"] = PowerState
            power_details.append(power_state)
        else:
            result = {'ret': False, 'msg': "response_system_url Error code %s" % response_system_url.status}
            REDFISH_OBJ.logout()
            return result

    result['ret'] = True
    result['entries'] = power_details
    # Logout of the current session
    REDFISH_OBJ.logout()
    return result


def main(ip, login_account, system_id):
    result = _get_power_state(ip, login_account, system_id)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])

main('192.168.10.22', 'xclarity', '')



