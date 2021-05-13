import asyncio
import base64
import hmac
import hashlib
# import random
# import string

from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device.aio import IoTHubDeviceClient
# from azure.iot.device import Message
# from azure.iot.device import MethodResponse
from azure.iot.device import exceptions

leaf_device_prefix = "leaf_device_"
leaf_model_identity = "dtmi:gatewayExample:myLeafDevice;1"

gateway_id = "my_Gateway"
gateway_model_id = "dtmi:gatewayExample:gateway;1"

id_scope = "0ne0005C8ED"
group_symmetric_key = "tzR2IDTirROdS3jg0KrYIs6j/+xTxgHYcs6EpYt/ibCpASN6nfX8vSMouw7LhcMGxAcmKUxVOkEhrYSaR1l8dA=="

provisioning_host = "global.azure-devices-provisioning.net"
terminate = False

device_list = {}

# derives a symmetric device key for a device id using the group symmetric key
def derive_device_key(device_id, group_symmetric_key):
    message = device_id.encode("utf-8")
    signing_key = base64.b64decode(group_symmetric_key.encode("utf-8"))
    signed_hmac = hmac.HMAC(signing_key, message, hashlib.sha256)
    device_key_encoded = base64.b64encode(signed_hmac.digest())
    return device_key_encoded.decode("utf-8")

async def connect_device(device_context):
    connection_retry_count = 1
    device_context["connected"] = False

    while (not device_context["connected"]) and (connection_retry_count < 3):
        device_context["device_symmetric_key"] = derive_device_key(device_context["device_id"], group_symmetric_key)

        provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
            provisioning_host=provisioning_host,
            registration_id=device_context["device_id"],
            id_scope=id_scope,
            symmetric_key=device_context["device_symmetric_key"],
            websockets=True
        )

        # DPS payload contains the model_id of the leaf device and the gateway identity to connect them to
        provisioning_device_client.provisioning_payload = ('{{"iotcModelId":"{}", "iotcGateway":{{"iotcGatewayId": "{}" }}}}').format(leaf_model_identity, gateway_id)
        device_context["registration_result"] = None
        try:
            device_context["registration_result"] = await provisioning_device_client.register()
        except exceptions.CredentialError:
            print("Credential Error")
        except exceptions.ConnectionFailedError: 
            print("Connection Failed Error")
        except exceptions.ConnectionDroppedError: # error if the key is wrong
            print("Connection Dropped Error")
        except exceptions.ClientError as inst: # error if the device is blocked
            print("ClientError")
        except Exception:
            print("Unknown Exception")

        if device_context["registration_result"] != None:
            print("The complete registration result is {}".format(device_context["registration_result"].registration_state))
            if device_context["registration_result"].status == "assigned":
                device_context["device_client"] = IoTHubDeviceClient.create_from_symmetric_key(
                    symmetric_key=device_context["device_symmetric_key"],
                    hostname=device_context["registration_result"].registration_state.assigned_hub,
                    device_id=device_context["device_id"],
                    websockets=True
                )

        # connect to IoT Hub
        try:
            await device_context["device_client"].connect()
            device_context["connected"] = True
        except:
            print("Connection failed, retry {} of 3".format(connection_retry_count))
            connection_retry_count = connection_retry_count + 1

async def main():

    # register the gateway device
    gateway_key = derive_device_key(gateway_id, group_symmetric_key)
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=gateway_id,
        id_scope=id_scope,
        symmetric_key=gateway_key,
        websockets=True
    )

    provisioning_device_client.provisioning_payload = ('{{"iotcModelId":"{}"}}').format(gateway_model_id)
    gateway_reg_result = None
    try:
        gateway_reg_result = await provisioning_device_client.register()
    except exceptions.CredentialError:
        print("Credential Error")
    except exceptions.ConnectionFailedError: 
        print("Connection Failed Error")
    except exceptions.ConnectionDroppedError: # error if the key is wrong
        print("Connection Dropped Error")
    except exceptions.ClientError as inst: # error if the device is blocked
        print("ClientError")
    except Exception:
        print("Unknown Exception")

    if gateway_reg_result != None:
        print("The complete gateway registration result is {}".format(gateway_reg_result.registration_state))

        # register the leaf devices and relate them to the gateway
        max_devices = 3
        for x in range(1, max_devices+1): 
            device_id = leaf_device_prefix + str(x)
            device_list[device_id] = {}
            device_list[device_id]["device_id"] = device_id
            await connect_device(device_list[device_id])

        #
        # Do something interesting here while the devices are connected
        #

        # finally, disconnect - won't get here because no good termination
        print("Disconnecting all devices from IoT Hub")
        for device_id in device_list:
            await device_list[device_id]["device_client"].disconnect()

# start the main routine
if __name__ == "__main__":
    asyncio.run(main())

    # If using Python 3.6 or below, use the following code instead of asyncio.run(main()):
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()