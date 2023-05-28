import paho.mqtt.client as mqtt
import json
import re
tracking = {}
def on_message(client, userdata, msg):
    msg_json = json.loads(msg.payload.decode('utf-8'))
    mac_address = msg_json['pc']['m2m:cin']['con']
    node = re.search(r'(?<=Mobius[/])(\w+)(?=[/]new_dev)', msg_json['to']).group(0)
    print(msg_json)
    #node_address = str(msg.payload)
    if tracking.get(mac_address):
        if tracking.get(mac_address) != node:
            print('Has changed!')
            mqttc.publish('/oneM2M/req/'+tracking.get(mac_address)+'_to_'+node+'/Mobius2/json', 1)
    else:
        tracking[mac_address] = node

mqttc = mqtt.Client()

mqttc.on_message = on_message
mqttc.connect('127.0.0.1')
mqttc.subscribe('/oneM2M/req/+/Mobius2/+',qos=0)

mqttc.loop_forever() 
