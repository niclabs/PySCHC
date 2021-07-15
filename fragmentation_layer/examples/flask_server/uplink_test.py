from flask import request
import base64
import json

from schc_handlers.schc_gateway_handler import SCHCGatewayHandler
from schc_protocols import SCHCProtocol

MTU = 51

### After reassembly callbacks ###

# print received message as ascii text
def process_print(msg):
    print("It works!")
    print(msg.decode("ascii"))

# save message to 'received.bin' file
def process_save2file(msg):
    with open("received.bin", "wb") as f:
        f.write(msg)
    print("Saved to received.bin")

handler = SCHCGatewayHandler(SCHCProtocol.LoRaWAN, MTU, process_save2file)

def receive_uplink():
    # Obtaining data from TTN requests
    data = request.get_json()
    downlink_url = request.headers["x-downlink-push"]
    fport = data["uplink_message"]["f_port"]
    dev_id = data["end_device_ids"]["device_id"]
    api_key = request.headers["x-downlink-apikey"]
    data = request.get_json()["uplink_message"]["frm_payload"]
    payload64 = data.encode("ascii")
    msg_bytes = base64.b64decode(payload64)

    # packet processing
    handler.handle(msg_bytes, fport, downlink_url, dev_id, api_key)
    return json.dumps({"Message": "Okay"}), 200