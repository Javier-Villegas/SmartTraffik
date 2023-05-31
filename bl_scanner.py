import paho.mqtt.client as paho
import re
from time import sleep
from hashlib import md5
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
    dev_list = msg_json["pc"]["m2m:uril"]
    id_list = []
    for dev in dev_list:
        node = re.search(r'(?<=Mobius[/]BTNode)(\w+)',dev)
        if node != None:
            id_list.append(int(node.group(0)))
    if ID in id_list:
        print('Reconnecting...')

    else:
        print('Register and create resources')
        topic_pub = "/oneM2M/req/"+AE_id + "/" +csi_mqtt + "/json"
        topic_reg = "/oneM2M/reg_req/"+AE_id + "/" +csi_mqtt + "/json"
        print('AE registration')
        client.publish(topic_reg,
                       json.dumps({'to':csi,'fr':AE_id,'rqi':rqi,'op':1,'ty':2,
                                   'pc':{'m2m:ae':{
                                        'rn':AE_id, 'api':'BluetoothDetector','rr':True                                       }}}))
        
        sleep(2)
        print('Container creation')
        
        print(json.dumps({'to':csi+'/'+AE_id,'fr':AE_id,'rqi':str(randint(0,100000)),'op':1,'ty':3,'pc':{'m2m:cnt':{'rn':'new_dev','mni':100}}}))#publish
        client.publish(topic_pub,
                       json.dumps({'to':csi+'/'+AE_id,'fr':AE_id,'rqi':str(randint(0,100000)),'op':1,'ty':3,'pc':{'m2m:cnt':{'rn':'new_dev','mni':100}}})) #publish
        sleep(2)
        # Creating subscription
        print('Subscription creation')
        sub_name = "New_dev_sub"
        #uri = ["http://10.10.10.114:7000?ct=json"]
        #uri = ["http://10.10.10.244:7000?ct=json"]
        #
        ##sub_msg = message_subscription_creation(common_msg,csi+"/"+rn+"/"+rn_cnt1,sub_name,uri)
        ##print("Sending creation sub message: ", sub_msg)

        #print(json.dumps({'to':csi+'/'+AE_id+'/'+'new_dev','fr':AE_id,'rqi':rqi,'op':1,'ty':23,
        #                           'pc':{'m2m:sub':{
        #                               'rn':sub_name,'nu':uri,'enc':{'net':[3]}, 'nct':1,
        #                               }}}))
        #client.publish(topic_pub,
        #               json.dumps({'to':csi+'/'+AE_id+'/'+'new_dev','fr':AE_id,'rqi':rqi,'op':1,'ty':23,
        #                           'pc':{'m2m:sub':{
        #                               'rn':sub_name,'enc':{'net':[3]},'nu':uri, 'nct':1,
        #                               }}})) #publish
        #sleep(2)
        #print('Subscription test')
        #client.publish(topic_pub,
        #               json.dumps({'to':csi,'fr':AE_id,'rqi':'1244','op':2,'fc':{'fu':1,'ty':23}}))
        #sleep(2) 
        #client.publish(topic_pub,
        #               json.dumps({'to':csi+'/'+AE_id+'/new_dev/New_dev_sub','fr':AE_id,'rqi':'1244','op':2,'fc':{'fu':1}}))
        #sleep(2) 


#define callback
def on_message(client, userdata, message):

    global ID
    print("received message from topic ",message.topic," =",str(message.payload.decode("utf-8")))
    print()
    #if(message.topic=="/oneM2M/resp/BTNodeInit/Mobius2"):
    #    msg_json = json.loads(message.payload.decode('utf-8'))
    #    dev_list = msg_json["pc"]["m2m:uril"]
    #    id_list = []
    #    for dev in dev_list:
    #        node = re.search(r'(?<=Mobius[/]BTNode)(\w+)',dev)
    #        if node != None:
    #            id_list.append(int(node.group(0)))
    #    print("Existing Nodes ID: ",id_list)
    #    if id_list:
    #        max_id = max(id_list)
    #    else:
    #        max_id = 0
    #    ID = max_id+1
    #    print("New Node ID: BTNode"+str(ID))



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
               json.dumps({'to':csi,'fr':AE_id,'rqi':AE_id,'op':2,'fc':{'fu':1,'ty':2}}))

sleep(5)

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

pub_msg = {'to':csi+'/'+AE_id+'/new_dev','fr':AE_id,'op':1,'rqi':rqi,'ty':4,'pc':{'m2m:cin':{'con':{}}}}
print(pub_msg)

with open('file.test','r+') as f:
    while True:
        sleep(0.1)

        newlines = f.readlines()
        if newlines:
            for newline in newlines:
                match = re.search(r'([0-9A-F]{2}[:-]){5}([0-9A-F]{2})',newline)
        
                if 'NEW' in newline:
                    mac = "0x" + match.group(0).replace(":","")
                    print(mac)
                    print(int(literal_eval(mac)))

                    print(f'[{datetime.now()}] New device: {match.group(0)} (md5: {md5(match.group(0).encode()).hexdigest()})')
                    pub_msg['rqi'] = str(randint(0,1000000))
                    pub_msg['pc']['m2m:cin']['con'] = int(mac,16)
                    client.publish(topic_pub, json.dumps(pub_msg))
                elif 'DEL' in newline:
                    print(f'[{datetime.now()}] Device deleted: {match.group(0)} (md5: {md5(match.group(0).encode()).hexdigest()})')
        else:
            f.truncate(0)
        


client.disconnect() #disconnect
client.loop_stop() #stop loop
