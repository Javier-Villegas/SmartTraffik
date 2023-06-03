import paho.mqtt.client as paho
import re
from time import sleep
from datetime import datetime
from ast import literal_eval
import time
import json
import sys
from random import randint

# Common values
broker="10.10.10.114"
#broker="127.0.0.1"
port=1883

global ID
ID = str(int(sys.argv[1].replace(":",""),16))


AE_id = "BTNode"+ID

AE_id_base = "BTNode"
csi = "Mobius" # CSE-ID
csi_mqtt = "Mobius2" # CSE-ID for MQTT topics
#rn = "maoriot-cse-in"
rqi = str(randint(0,100000))


def on_discovery_resp(client,userdata,message):
    global ID
    print("received message from topic ",message.topic," =",str(message.payload.decode("utf-8")))
    print()
    msg_json = json.loads(message.payload.decode('utf-8'))
    if msg_json.get('pc') and msg_json['pc'].get('m2m:uril'):
        dev_list = msg_json["pc"]["m2m:uril"]
    else:
        dev_list = []
    id_list = []
    print(dev_list)
    for dev in dev_list:
        node = re.search(r'(?<=Mobius[/]BTNode)(\w+)',dev)
        if node != None:
            id_list.append(int(node.group(0)))
    if int(ID) in id_list:
        print('Reconnecting...')

    else:
        print('Register and create resources')
        topic_pub = "/oneM2M/req/"+AE_id + "/" +csi_mqtt + "/json"
        topic_reg = "/oneM2M/reg_req/"+AE_id + "/" +csi_mqtt + "/json"
        print('AE registration')
        client.publish(topic_reg,
                       json.dumps({'to':csi,'fr':AE_id,'rqi':str(randint(0,100000)),'op':1,'ty':2,
                                   'pc':{'m2m:ae':{
                                        'rn':AE_id, 'api':'BluetoothDetector','rr':True                                       }}}))
        
        print('Container creation')
        
        # New devs
        client.publish(topic_pub,
                       json.dumps({'to':csi+'/'+AE_id,'fr':AE_id,'rqi':str(randint(0,100000)),'op':1,'ty':3,'pc':{'m2m:cnt':{'rn':'new_dev','mni':100}}})) #publish
        # Del devs
        client.publish(topic_pub,
                       json.dumps({'to':csi+'/'+AE_id,'fr':AE_id,'rqi':str(randint(0,100000)),'op':1,'ty':3,'pc':{'m2m:cnt':{'rn':'del_dev','mni':100}}})) #publish


#define callback
def on_message(client, userdata, message):

    global ID
    print("received message from topic ",message.topic," =",str(message.payload.decode("utf-8")))
    print()


# Common message structure
common_msg = {}

common_msg["to"]=csi
common_msg["fr"]=AE_id_base+"init"
common_msg["rqi"]=rqi



client= paho.Client("client-001") #create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")
client.message_callback_add('/oneM2M/resp/BTNodeInit/Mobius2',on_discovery_resp)
######Bind function to callback
client.on_message=on_message
#####




# Initial discovery of AEs in prder to give an ID to  this AE if first time

print("connecting to broker ",broker)
print()

client.connect(broker,port)#connect
client.loop_start() #start loop to process received messages


topic_init_sub = "/oneM2M/resp/"+AE_id_base+"Init/+"
topic_sub1 = "/oneM2M/resp/"+AE_id+"/+"
topic_sub2 = "/oneM2M/req/+/"+AE_id+"/+"
topic_sub3 = "/oneM2M/reg_resp/"+AE_id+"/+"
client.subscribe(topic_init_sub) #subscribe
client.subscribe(topic_sub1) #subscribe
client.subscribe(topic_sub2)
client.subscribe(topic_sub3)
client.publish('/oneM2M/req/BTNodeInit/Mobius2/json',
               json.dumps({'to':csi,'fr':AE_id,'rqi':AE_id+'Init','op':2,'fc':{'fu':1,'ty':2}}))


#AE_id = AE_id_base + str(ID)

rn = AE_id

common_msg["fr"]=AE_id


###############
# Registration



topic_pub = "/oneM2M/req/"+AE_id + "/" +csi_mqtt + "/json"
topic_reg = "/oneM2M/reg_req/"+AE_id + "/" +csi_mqtt + "/json"



client.subscribe(topic_sub1) #subscribe
client.subscribe(topic_sub2)
client.subscribe(topic_sub3)

##########
# use "def message_resource_creation(common_msg,to,content):" to send the devices to Mobius





time.sleep(4)

new_msg = {'to':csi+'/'+AE_id+'/new_dev','fr':AE_id,'op':1,'rqi':rqi,'ty':4,'pc':{'m2m:cin':{'con':{}}}}
del_msg = new_msg.copy()
del_msg['to'] = f'{csi}/{AE_id}/del_dev'

with open('file.test','r+') as f:
    while True:
        sleep(0.1)

        newlines = f.readlines()
        if newlines:
            for newline in newlines:
                match = re.search(r'([0-9A-F]{2}[:-]){5}([0-9A-F]{2})',newline)
        
                if 'NEW' in newline:
                    mac = "0x" + match.group(0).replace(":","")
                    print(f'[{datetime.now()}] New device: {match.group(0)}')
                    new_msg['rqi'] = str(randint(0,1000000))
                    new_msg['pc']['m2m:cin']['con'] = int(mac,16)
                    client.publish(topic_pub, json.dumps(new_msg))
                elif 'DEL' in newline:
                    mac = "0x" + match.group(0).replace(":","")
                    print(f'[{datetime.now()}] Device deleted: {match.group(0)}')
                    del_msg['rqi'] = str(randint(0,1000000))
                    del_msg['pc']['m2m:cin']['con'] = int(mac,16)
                    client.publish(topic_pub, json.dumps(del_msg))
        else:
            f.truncate(0)
        


client.disconnect() #disconnect
client.loop_stop() #stop loop
