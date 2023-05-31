from paho.mqtt.client import Client
import json
from time import sleep
from random import randint


def on_discovery(client, userdata, message):
    print(message.topic)
    print(message.payload)
    msg = json.loads(message.payload)
    for item in msg['pc']['m2m:uril']:
        client.subscribe()
        print(item)

def on_message(client, userdata, message):
    print(message.topic)
    print(message.payload)


server_address = '10.10.10.114'
csi = 'Mobius'
AE_id = 'RIC-test'


client = Client()
client.connect(server_address)
client.on_message = on_message
client.subscribe('/oneM2M/resp/+/Mobius2/+')
client.message_callback_add('/oneM2M/resp/+/Mobius2/+',on_discovery)


j = json.dumps({'to':csi,'fr':AE_id,'rqi':AE_id,'op':2,'fc':{'fu':1,'ty':2}})
print(j)
client.publish('/oneM2M/req/MAORIOT-AE/Mobius2/json',
               json.dumps({'to':'Mobius/MAORIOT-AE','fr':AE_id,'rqi':str(randint(0,10000)),'op':2,'fc':{'fu':1,'ty':3}}))

sleep(1)
client.loop_forever()




