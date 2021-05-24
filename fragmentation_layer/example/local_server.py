import base64
import json
from flask import Flask, request
from common_methods import MTU, send_socket
from schc_handlers import SCHCGatewayHandler
from schc_protocols import SCHCProtocol

SENDER_PORT = 50007

app = Flask(__name__)

handler = SCHCGatewayHandler(SCHCProtocol.LoRaWAN, MTU)
queue = list()


@app.route("/test", methods=['POST'])
def execute_test():
    data = request.get_json()
    fport = data["port"]
    dev_id = data["dev_id"]
    downlink_url = data["downlink_url"]
    print(fport, dev_id, downlink_url)
    msg_bytes = base64.b64decode(data["payload_raw"].encode("utf-8"))
    handler.handle(msg_bytes, fport, downlink_url, dev_id)
    return json.dumps({"Message": "Okay"}), 200


@app.route("/to_socket", methods=['POST'])
def sent_to_socket():
    data = request.get_json()
    to_send = bytes([data["port"]]) + base64.b64decode(data["payload_raw"].encode("utf-8"))
    queue.append(to_send)
    try:
        candid = queue[0]
        send_socket(candid, SENDER_PORT)
        print(queue.pop(0))
    except ConnectionRefusedError:
        pass
    return {}, 200


if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
