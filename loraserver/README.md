# Lora Network Server

This application is a UDP server that listens for lora Uplink packets from the LoRa Packet forwader, and forwards the message to Watson Iot Via MQTT, it is also capable of sending downlink messages back to the gateway which then propagates the lora packet to the lora devices.  

## Run the app locally

1. [Install Python][]
1. cd into this project's root directory
1. Run `pip install -r requirements.txt` to install the app's dependencies
1. Run `python loraserver.py`


[Install Python]: https://www.python.org/downloads/
