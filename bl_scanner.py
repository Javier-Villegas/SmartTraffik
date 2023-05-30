import paho.mqtt.client as paho
import re
from time import sleep
from hashlib import md5
from datetime import datetime
from ast import literal_eval
import time
import json

# Common values
broker="10.10.10.114"
#broker="127.0.0.1"
port=1883

global ID
ID = None

AE_id_base = "BTNode"
csi = "Mobius" # CSE-ID
csi_mqtt = "Mobius2" # CSE-ID for MQTT topics
#rn = "maoriot-cse-in"
rqi = "test_rqi"



def message_register(common_msg,to,rn,api):
        msg = common_msg.copy()
        msg["op"] = 1	#operation: create
        msg["ty"] = 2	#type: ae

        pc = {}

        ae = {}
        ae["rn"] = rn
        ae["api"] = api
        ae["rr"] = True

        pc["m2m:ae"] = ae

        msg["pc"] = pc

        msg_json = json.dumps(msg)

        print("Message for registering ae: ",msg_json)
        print()
        return msg_json

def message_container_creation(common_msg,to,rn,mni):
	msg = common_msg.copy()
	msg["to"] = to
	msg["op"] = 1
	msg["ty"] = 3  # container
	pc = {}

	cnt = {}
	cnt["rn"] = rn
	cnt["mni"] = mni

	pc["m2m:cnt"] = cnt

	msg["pc"] = pc

	msg_json = json.dumps(msg)

	print("Message for registering container: ",msg_json);print();
	return msg_json


def message_resource_creation(common_msg,to,content):
        msg = common_msg.copy()
        msg["to"] = to
        msg["op"] = 1
        msg["ty"] = 4  # content instance
        pc = {}

        cin = {}
        cin["con"] = content

        pc["m2m:cin"] = cin

        msg["pc"] = pc

        msg_json = json.dumps(msg)

        print("Message for creating resource: ",msg_json)
        print()

        return msg_json


def message_subscription_creation(common_msg,to,sub_name,uri):
        msg = common_msg.copy()
        msg["to"] = to
        msg["op"] = 1
        msg["ty"] = 23 # content instance
        pc = {}

        sub = {}
        sub["rn"] = sub_name

        enc = {}
        enc["net"] = [3]

        sub["enc"] = enc
        sub["nu"] = uri
        sub["nct"] = 1

        pc["m2m:sub"] = sub

        msg["pc"] = pc

        msg_json = json.dumps(msg)

        print("Message for creating resource: ",msg_json)
        print()

        return msg_json



def message_discover(common_msg,to,fc):
        msg = common_msg.copy()
        msg["op"] = 2   #operation: retrieve
        msg["to"] = to

        msg["fc"] = fc


        msg_json = json.dumps(msg)

        print("Message for discover: ",msg_json)
        print()

        return msg_json


#define callback
def on_message(client, userdata, message):

    global ID
    print("received message from topic ",message.topic," =",str(message.payload.decode("utf-8")))
    print()
    if(message.topic=="/oneM2M/resp/BTNodeInit/Mobius2"):
        msg_json = json.loads(message.payload.decode('utf-8'))
        dev_list = msg_json["pc"]["m2m:uril"]
        id_list = []
        for dev in dev_list:
            node = re.search(r'(?<=Mobius[/]BTNode)(\w+)',dev)
            if node != None:
                id_list.append(int(node.group(0)))
        print("Existing Nodes ID: ",id_list)
        if id_list:
            max_id = max(id_list)
        else:
            max_id = 0
        ID = max_id+1
        print("New Node ID: BTNode"+str(ID))



# Common message structure
common_msg = {}

common_msg["to"]=csi
common_msg["fr"]=AE_id_base+"init"
common_msg["rqi"]=rqi



client= paho.Client("client-001") #create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")
######Bind function to callback
client.on_message=on_message
#####




# Initial discovery of AEs in prder to give an ID to  this AE if first time

print("connecting to broker ",broker)
print()

client.connect(broker,port)#connect
client.loop_start() #start loop to process received messages


try:
    with open("ID.json") as f:
        id_json = json.loads(f)
        print(id_json);print();
        ID = id_json["id"]
        new_Node = False
except:
    print("This device has no ID")
    print("Updating device ID...");print()

    topic_init_pub = "/oneM2M/req/"+AE_id_base+"Init/" + csi_mqtt + "/json"
    topic_init_sub = "/oneM2M/resp/"+AE_id_base+"Init/+"
    # Initial discovery of AEs in prder to give an ID to  this AE if first time



    client.subscribe(topic_init_sub) #subscribe

    # Create retrieve message for discovery
    fc = {}
    fc["fu"]=1
    fc["ty"]=2

    rve_msg = message_discover(common_msg,csi,fc)
    while(ID == None):
        client.publish(topic_init_pub,rve_msg) #publish
        time.sleep(5)

    # Save new ID in ID.json file
    print("Saving new ID in ID.josn file...")
    with open("ID.json","w") as f:
        json_id = {}
        json_id["id"] = ID
        f.write(json.dumps(json_id))
        print("New ID saved!")

    client.unsubscribe(topic_init_sub)

    new_Node = True

    client.unsubscribe(topic_init_sub)



AE_id = AE_id_base + str(ID)

rn = AE_id

common_msg["fr"]=AE_id


###############
# Registration

topic_sub1 = "/oneM2M/resp/"+AE_id+"/+"
topic_sub2 = "/oneM2M/req/+/"+AE_id+"/+"
topic_sub3 = "/oneM2M/reg_resp/"+AE_id+"/+"


topic_pub = "/oneM2M/req/"+AE_id + "/" +csi_mqtt + "/json"
topic_reg = "/oneM2M/reg_req/"+AE_id + "/" +csi_mqtt + "/json"



client.subscribe(topic_sub1) #subscribe
client.subscribe(topic_sub2)
client.subscribe(topic_sub3)

rn_cnt1 = "new_dev"
rn_cnt2 = "lost_dev"

if(new_Node == True):

    api = "BluetoothDetector"
    crt_msg = message_register(common_msg,csi,rn,api)

    # Publish
    print("Registering: ", crt_msg)
    print()
    client.publish(topic_reg,crt_msg) #publish
    time.sleep(1)


    mni = 100
    cnt_msg1 = message_container_creation(common_msg,csi+"/"+rn,rn_cnt1,mni)
    cnt_msg2 = message_container_creation(common_msg,csi+"/"+rn,rn_cnt2,mni)
    client.publish(topic_pub,cnt_msg1) #publish
    time.sleep(1)

    client.publish(topic_reg,cnt_msg2) #publish

    time.sleep(1)

    # Creating subscription
    sub_name = "New_dev_sub"
    uri = ["http://127.0.0.1:7000?ct=json"]
    
    sub_msg = message_subscription_creation(common_msg,csi+"/"+rn+"/"+rn_cnt1,sub_name,uri)
    print("Sending creation sub message: ", sub_msg)
    client.publish(topic_pub,sub_msg)

    time.sleep(2)

    # Checking if the subscription has been created
    fc = {}
    fc["fu"]=1
    fc["ty"]=23
    common_msg["rqi"]="1244"

    rve_msg = message_discover(common_msg,csi,fc)
    client.publish(topic_pub,rve_msg)
    time.sleep(1)



##########
# use "def message_resource_creation(common_msg,to,content):" to send the devices to Mobius





time.sleep(4)

pub_msg = json.loads(message_resource_creation(common_msg,csi+'/'+AE_id+'/'+rn_cnt1,[]))
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
                    pub_msg['pc']['m2m:cin']['con'] = int(literal_eval(mac))
                    client.publish(topic_pub, json.dumps(pub_msg))
                elif 'DEL' in newline:
                    print(f'[{datetime.now()}] Device deleted: {match.group(0)} (md5: {md5(match.group(0).encode()).hexdigest()})')
        else:
            f.truncate(0)
        


client.disconnect() #disconnect
client.loop_stop() #stop loop
