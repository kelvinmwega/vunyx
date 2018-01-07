#
# Purpose:
#     Lora Network server. Implements UDP server that listens for udp packets from semtech packet forwarder application
#     received data is sent to IBM watson IoT via mqtt, the code is configured as a gateway.
#
# Author :
#     Kelvin Mwega - kelvinmk@ke.ibm.com
#
# Hardware :
#     Built By : Reha Yurdakul - rehay@ke.ibm.com
#     Raspberry Pi 3.
#     IMST IC880A Concentrator.
#
# Version 1 : 15.May.2017 by kelvinmk@ke.ibm.com
#     - UDP server implemented and tested
#
# Version 2 : 16.May.2017 by kelvinmk@ke.ibm.com
#     - Configured as a gateway to watson IoT.
#     - received UDP data sent to watdson IoT via MQTTself.
#
# Version 3 : 27.May.2017 by kelvinmk@ke.ibm.com
#     - Modified to send back acknowledgement packet to packet forwarder applicationself.


import socket
import sys
import binascii
import ibmiotf.gateway
import json
import array
import time
import os,binascii
from flask import Flask, jsonify
import cogs as cog

# Organization ID 14br69
# Device Type LoRaGW
# Device ID   LoRaGW01
# Authentication Method   token
# Authentication Token    vunyxloragw

dataEncoded = None
port = int(os.getenv('PORT', 8000))
app = Flask(__name__)
########## Watson IoT MQTT Functions ###########

def myOnPublishCallback():
       print("Confirmed event received by IBM Watson IoT Platform\n")
       print >>sys.stderr, '##############################################'
       print >>sys.stderr, '\nwaiting to receive message'


########## Utilities ###########

def int_to_bytes(value, length):
    result = []

    for i in range(0, length):
        result.append(value >> (i * 8) & 0xff)

    result.reverse()

    return result

def HexToByte( hexStr ):
    bytes = []

    hexStr = ''.join( hexStr.split(" ") )

    for i in range(0, len(hexStr), 2):
        bytes.append( chr( int (hexStr[i:i+2], 16 ) ) )

    return ''.join( bytes )

def pktSentConfirm(msgTx):
    #msgRx
    if (checkNodeAddress(msgTx) == True):
        print "Not my message " + msgTx.decode('base64').split(',')[0]  + "  " + respConstructor(msgTx).split(',')[0]
        return True

    print "My message " + msgTx.decode('base64')
    return False

def respConstructor(msgRx):

    try:
        strToReturn = "GW01," + msgRx.decode('base64').split(',')[0]
    except:
        strToReturn = "GW01,EP002"

    return strToReturn

def checkNodeAddress(nodeId):
    print "########## " + nodeId.decode('base64').split(',')[0]
    checkNodeAddressCdt(nodeId)
    nodesArray = ["EP001", "EP002", "EP003", "TestNode5", "GPSNode", "AR1"]

    if nodeId.decode('base64').split(',')[0] in nodesArray:
        dataString = ("GW01," + str(nodeId.decode('base64').split(',')[0])).encode('base64')
        global dataEncoded
        dataEncoded = dataString
        print dataString
        return True

    return False

def checkNodeAddressCdt(nodeId):
    try:
        cog.getDev(nodeId.decode('base64').split(',')[0])
    except Exception as e:
        pass


def postToWatsonIoT(pktTProcess):

    objToSend = json.loads(pktTProcess)
    nodeIdentifier = json.loads(pktTProcess)['rxpk'][0]['data'].decode('base64').split(',')[0]
    nodeData01 = json.loads(pktTProcess)['rxpk'][0]['data'].decode('base64').split(',')[1]

    objToSend['rxpk'][0]['nodeID'] = nodeIdentifier
    objToSend['rxpk'][0]['nodeData01'] = nodeData01

    print (objToSend)

    gatewaySuccess = gatewayCli.publishGatewayEvent("event", "json", objToSend, qos=1, on_publish=myOnPublishCallback )
    deviceSuccess = gatewayCli.publishDeviceEvent("Everporimeter", nodeIdentifier, "event", "json", objToSend, qos=1, on_publish=myOnPublishCallback )

    if not gatewaySuccess:
        print("Gateway not connected to IBM Watson IoT Platform while publishing from Gateway")

    if not deviceSuccess:
        print("Gateway not connected to IBM Watson IoT Platform while publishing from Gateway on behalf of a device")


########## Handlers ###########

def respondPushAck():
    dataAck = bytearray()




if __name__ == '__main__':
    #>>> binascii.hexlify(bytearray(array_alpha))
    # Create a TCP/IP socket

    UDP_IP_ADDRESS = "localhost"
    UDP_PORT_NO = 1680

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    organization = "14br69"
    gatewayType = "LoRaGW"
    gatewayId = "LoRaGW01"

    authMethod = "token"
    authToken = "vunyxloragw"
    gatewayOptions = {"org": organization, "type": gatewayType, "id": gatewayId, "auth-method": authMethod, "auth-token": authToken}
    gatewayCli = ibmiotf.gateway.Client(gatewayOptions)

    gatewayCli.connect()

    # Bind the socket to the port
    server_address = ('0.0.0.0', 1690)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)
    app.run(host='0.0.0.0', port=port, debug=True)
    pullAddress = None
    pullTocken = None
    pullGatewayId = None

    #sent = sock.sendto("test", (UDP_IP_ADDRESS, UDP_PORT_NO))

    while True:
        try :
            dataAck = bytearray()
            dataResp = bytearray()
            data, address = sock.recvfrom(4096)
            data = bytearray(buffer(data))

            protVersion = data[0]
            token = data[1:3]
            identifier = data[3]
            gwID = data[4:12]
            rawData = data[12:]

            print str(data)

            if str(identifier) == "0":
                try:

                    txPkt = {}
                    pktToRsp = {}
                    dataToSend = rawData.decode("utf-8")
                    #gatewayCli.setMessageEncoderModule('json', jsonCodec)
                    rxPkt = json.loads(dataToSend)
                    rxPktArray = rxPkt['rxpk'][0]

                    dataAck.extend(int_to_bytes(protVersion, 1))
                    dataAck.extend(token)
                    dataAck.extend(int_to_bytes(1, 1))

                    if dataAck:
                        #sent = sock.sendto(data, address)
                        sent = sock.sendto(buffer(dataAck), address)
                        print >>sys.stderr, 'sent PUSH_ACK %s bytes back to %s' % (sent, address)

                    if (pktSentConfirm(rxPktArray['data']) == True):

                        postToWatsonIoT(dataToSend)

                        pktToRsp['imme'] = True
                        pktToRsp['freq'] = rxPktArray['freq']
                        pktToRsp['rfch'] = 0
                        pktToRsp['powe'] = 14
                        pktToRsp['modu'] = 'LORA'
                        pktToRsp['datr'] = rxPktArray['datr']
                        pktToRsp['codr'] = rxPktArray['codr']
                        pktToRsp['ipol'] = False
                        #pktToRsp['prea'] = 8
                        pktToRsp['size'] = 10
                        pktToRsp["data"] = dataEncoded.strip()
                        txPkt['txpk'] = pktToRsp

                        #print(txPkt)
                        #print "#########  " + rxPktArray['data'] + " --- " + pktToRsp['data'] + " --- " + pktToRsp['data'].decode('base64')
                        time.sleep(2)

                        try: #Check for PULL_ACK

                            pullTocken = HexToByte(binascii.b2a_hex(os.urandom(2)))
                            dataResp.extend(int_to_bytes(protVersion, 1))
                            dataResp.extend(pullTocken)
                            dataResp.extend(int_to_bytes(3, 1))
                            dataResp.extend(json.dumps(txPkt))

                            #print dataResp[0]
                            #print dataResp[1:3]
                            #print dataResp[3]
                            #print dataResp[4:]
                            #print json.dumps(pktToRsp)

                            sent = sock.sendto(buffer(dataResp), pullAddress)
                            print >>sys.stderr, 'sent PULL_RESP %s bytes back to %s' % (sent, pullAddress)

                        except Exception as e:
                            pass

                except Exception as e:

                    print e
                    rxPktArray = rxPkt['stat']
                    print rxPktArray

            elif str(identifier) == "2":
                dataAck.extend(int_to_bytes(protVersion, 1))
                dataAck.extend(token)
                dataAck.extend(int_to_bytes(4, 1))

                #print(buffer(dataAck))

                if dataAck:
                    #sent = sock.sendto(data, address)
                    sent = sock.sendto(buffer(dataAck), address)
                    print >>sys.stderr, 'sent PULL_ACK %s bytes back to %s' % (sent, address)
                    pullAddress = address
                    pullTocken = token
                    pullGatewayId = gwID

            elif str(identifier) == "5":

                dataAck.extend(int_to_bytes(protVersion, 1))
                dataAck.extend(token)
                dataAck.extend(int_to_bytes(4, 1))

                #print >>sys.stderr, '##### received %s bytes from %s' % (len(data), address)
                print >>sys.stderr, ("Protocol Version -- " + str(protVersion))
                print >>sys.stderr, ("Token -- " + str(binascii.hexlify(token)))
                print >>sys.stderr, ("Identifier -- ") + str(identifier)
                # print >>sys.stderr, ("Gateway ID -- " + str(binascii.hexlify(gwID)))
                # print >>sys.stderr, ("LoRa Payload --" + rawData )
        except:
            raise
            # print "got something!!"

        # except KeyboardInterrupt :
        #     break

    print("\nLogging off....")
