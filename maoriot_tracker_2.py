import paho.mqtt.client as mqtt
import json
import re
from random import randint
tracking = {}
subscriptions = set()
def on_discovery(client,userdata,msg):
    print(msg.topic)
    print(msg.payload)
    msg_json = json.loads(msg.payload.decode('utf-8'))
    for uri in set(msg_json['pc']['m2m:uril']).difference(subscriptions):
        mqttc.subscribe(f'/oneM2M/req/{uri.split("/")[1]}/Mobius2/+')
        mqttc.message_callback_add(f'/oneM2M/req/{uri.split("/")[1]}/Mobius2/+',on_message)
        subscriptions.add(uri)

def on_message(client, userdata, msg):
    print(msg.topic)
    print(msg.payload)
    msg_json = json.loads(msg.payload.decode('utf-8'))
    mac_address = msg_json['pc']['m2m:cin']['con']
    node = re.search(r'(?<=Mobius[/])(\w+)(?=[/]new_dev)', msg_json['to']).group(0)
    print(msg_json)
    print(node)
    print(mac_address)
    #node_address = str(msg.payload)
    if tracking.get(mac_address):
        if tracking.get(mac_address) != node:
            print('Has changed!')
            mqttc.publish('/oneM2M/req/'+tracking.get(mac_address)+'_to_'+node+'/Mobius2/json', 1)
    tracking[mac_address] = node


csi = "Mobius" # CSE-ID
csi_mqtt = "Mobius2" # CSE-ID for MQTT topics
mqttc = mqtt.Client()

mqttc.on_message = on_message
mqttc.connect('10.10.10.114')
mqttc.subscribe('/oneM2M/resp/BTNodeInit/Mobius2')
mqttc.message_callback_add('/oneM2M/resp/BTNodeInit/Mobius2',on_discovery)
mqttc.publish('/oneM2M/req/BTNodeInit/Mobius2/json',
               json.dumps({'to':csi,'fr':'MAORIOT-AE','rqi':str(randint(0,1000)),'op':2,'fc':{'fu':1,'ty':2}}))

#mqttc.subscribe('/oneM2M/req/+/Mobius2/+',qos=0)

mqttc.loop_forever() 
