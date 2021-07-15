from flask import Flask, make_response, request
import os
import sys
from uplink_test import receive_uplink
import logging
import socket

app_server = Flask(__name__)

logging.basicConfig(filename='error.log', level=logging.DEBUG)

@app_server.route("/uplink", methods=["POST"])
def uplink():
    return receive_uplink()

print("Starting...")

if __name__ == '__main__':
    app_server.run(host="0.0.0.0", port=5000)
