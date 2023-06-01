import paho.mqtt.client as mqtt
import json
import re
from random import randint
import time
tracking = {}
subscriptions = set()
pairs = set()





# Tal y, el último nodo que se registre no se guardará aquí  (si se registra despés de que esto esté lanzado)
def on_discovery(client,userdata,msg):
    print(msg.topic)
    print(msg.payload)
    msg_json = json.loads(msg.payload.decode('utf-8'))
    registered = False
    for uri in set(msg_json['pc']['m2m:uril']).difference(subscriptions):
        if(uri == "Mobius/MAORIOT-AE"):
            registered = True
        elif("BTNode" in uri):
            #mqttc.subscribe(f'/oneM2M/req/{uri.split("/")[1]}/Mobius2/+')
            #mqttc.message_callback_add(f'/oneM2M/req/{uri.split("/")[1]}/Mobius2/+',on_message_mac)
            # Create subscription
            mqttc.publish('/oneM2M/req/MAORIOT-AE/Mobius2/json',
                          json.dumps({'to': uri+"/new_dev",'fr': 'MAORIOT-AE','rqi': str(randint(0,10000)),'op':1,'ty':23,
                                   'pc':{'m2m:sub':{
                                        'rn': 'New_dev_sub','nu': ["mqtt:/MAORIOT-AE"] , 'nct':1,
                                        'enc':{
                                            'net':[3],
                                        }}}}))
            subscriptions.add(uri)
    
    if(registered == False):
        mqttc.publish('/oneM2M/reg_req/MAORIOT-AE/Mobius2/json',
                      json.dumps({'to': "Mobius",'fr': 'MAORIOT-AE','rqi': str(randint(0,10000)),'op':1,'ty':2,
                                   'pc':{'m2m:ae':{
                                        'rn': 'MAORIOT-AE', 'api':'Dev_tracker','rr':True}}}))
        

# esta función ya no se usa
def on_message_mac(client, userdata, msg):
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
            rn = tracking.get(mac_address)+'_to_'+node
            if(rn not in pairs):
                mqttc.publish('/oneM2M/req/MAORIOT-AE/Mobius2/json',
                              json.dumps({'to': "Mobius/MAORIOT-AE",'fr': 'MAORIOT-AE','rqi': str(randint(0,10000)),'op':1,'ty':3,
                                   'pc':{'m2m:cnt':{
                                        'rn': rn, 'mni':200}}}))
                time.sleep(1)
            
            mqttc.publish('/oneM2M/req/MAORIOT-AE/Mobius2/json',
                              json.dumps({'to': "Mobius/MAORIOT-AE/"+rn,'fr': 'MAORIOT-AE','rqi': str(randint(0,10000)),'op':1,'ty':4,
                                   'pc':{'m2m:cin':{
                                        'con': 1}}}))
            #mqttc.publish('/oneM2M/req/'+tracking.get(mac_address)+'_to_'+node+'/Mobius2/json', 1)
    tracking[mac_address] = node

def on_message(client, userdata, msg):
    print(msg.topic)
    print(msg.payload)
    
    msg_json = json.loads(msg.payload.decode('utf-8'))

    

    if(msg_json['rqi']=="discover_pairs"):
        for uri in set(msg_json['pc']['m2m:uril']).difference(pairs):
            if("_to_" in uri):
                pairs.add(uri)

    elif("m2m:sgn" in msg_json["pc"]):
        # Publish ack
        mqttc.publish('/oneM2M/resp/Mobius2/MAORIOT-AE/json',
                      json.dumps({'to': 'Mobius', 'fr': 'MAORIOT-AE', 'rqi': msg_json['rqi'], 'rsc': 2000 })) # rsc: 2xxx request received and done, 1xxx request received but in progress
          
        mac_address = msg_json['pc']['m2m:sgn']['nev']['rep']['m2m:cin']['con']
        #node = re.search(r'(?<=Mobius[/])(\w+)(?=[/]new_dev)', msg_json['to']).group(0)
        node = msg_json['pc']['m2m:sgn']['nev']['rep']['m2m:cin']['cr']
        print(msg_json)
        print(node)
        print(mac_address)
        #node_address = str(msg.payload)
        if tracking.get(mac_address):
            if tracking.get(mac_address) != node:
                print('Has changed!')
                rn = tracking.get(mac_address)+'_to_'+node
                if(rn not in pairs):
                    mqttc.publish('/oneM2M/req/MAORIOT-AE/Mobius2/json',
                                json.dumps({'to': "Mobius/MAORIOT-AE",'fr': 'MAORIOT-AE','rqi': str(randint(0,10000)),'op':1,'ty':3,
                                    'pc':{'m2m:cnt':{
                                            'rn': rn, 'mni':200}}}))
                    time.sleep(1)
                
                mqttc.publish('/oneM2M/req/MAORIOT-AE/Mobius2/json',
                                json.dumps({'to': "Mobius/MAORIOT-AE/"+rn,'fr': 'MAORIOT-AE','rqi': str(randint(0,10000)),'op':1,'ty':4,
                                    'pc':{'m2m:cin':{
                                            'con': 1}}}))
                #mqttc.publish('/oneM2M/req/'+tracking.get(mac_address)+'_to_'+node+'/Mobius2/json', 1)
        tracking[mac_address] = node

    
    



csi = "Mobius" # CSE-ID
csi_mqtt = "Mobius2" # CSE-ID for MQTT topics
mqttc = mqtt.Client()

mqttc.on_message = on_message
mqttc.connect('10.10.10.114')

mqttc.subscribe('/oneM2M/reg_resp/MAORIOT-AE/+')
mqttc.subscribe('/oneM2M/resp/MAORIOT-AE/+')
mqttc.subscribe('/oneM2M/req/+/MAORIOT-AE/+')







mqttc.subscribe('/oneM2M/resp/BTNodeInit/Mobius2')
mqttc.message_callback_add('/oneM2M/resp/BTNodeInit/Mobius2',on_discovery)
mqttc.publish('/oneM2M/req/BTNodeInit/Mobius2/json',
               json.dumps({'to':csi,'fr':'MAORIOT-AE','rqi':str(randint(0,1000)),'op':2,'fc':{'fu':1,'ty':2}}))

mqttc.publish('/oneM2M/req/MAORIOT-AE/Mobius2/json',
              json.dumps({'to':csi+'/MAORIOT-AE','fr':'MAORIOT-AE','rqi':"discover_pairs",'op':2,'fc':{'fu':1,'ty':3}}))

#mqttc.subscribe('/oneM2M/req/+/Mobius2/+',qos=0)

mqttc.loop_forever() 
