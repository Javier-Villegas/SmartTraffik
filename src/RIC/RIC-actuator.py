from paho.mqtt.client import Client
import json
import sys
from time import sleep
from random import randint

def on_ric_discovery(client, userdata, message):
    print()
    print('ric discovery')
    print(message.topic)
    print(message.payload)
    msg = json.loads(message.payload)
    if msg.get('pc') and msg['pc'].get('m2m:uril'):
        if AE_id not in msg['pc']['m2m:uril']:
            client.publish(f'/oneM2M/reg_req/{AE_id}/Mobius2/json',
                       json.dumps({'to':csi,
                                   'fr':AE_id,
                                   'rqi':AE_id+str(int(randint(0,10000))),
                                   'op':1,
                                   'ty':2,
                                   'pc':{'m2m:ae':{
                                        'rn':AE_id,
                                        'api':'RIC-Actuator',
                                        'rr':True
                                       }}}))
            client.publish(f'/oneM2M/req/{AE_id}/Mobius2/json',
                           json.dumps({'to':f'{csi}/{AE_id:}',
                                   'fr':AE_id,
                                   'rqi':AE_id+str(int(randint(0,10000))),
                                   'op':1,
                                   'ty':3,
                                   'pc':{'m2m:cnt':{
                                        'rn':'cell_status',
                                        'mni':100
                                       }}}))
        else:
            print('Reconnecting')




def on_discovery(client, userdata, message):
    print()
    print('on discovery')
    print(message.topic)
    print(message.payload)
    msg = json.loads(message.payload)
    # Container request
    if msg.get('rqi') == rqi:
        print(msg['pc']['m2m:uril'])
        if msg.get('pc') and msg['pc'].get('m2m:uril'):
            print(watch_pair)
            containers = list(filter(lambda x: watch_pair[0] in x or watch_pair[1] in x,
                                 msg['pc']['m2m:uril']))
            if len(containers) != 2:
                print('Tracking path does not exist')
                exit(1)
            client.publish(f'/oneM2M/req/{AE_id}/Mobius2/json',
                       json.dumps({'to':containers[0],
                                  'fr':AE_id,
                                  'op':1,
                                  'ty':2,
                                  'rqi':f'{AE_id}_{str(randint(0,100000))}',
                                  'pc':{ 'm2m:sub':{
                                      'rn': 'sub',
                                      'nu': [f'mqtt:/{AE_id}'],
                                      'nct':1,
                                      'enc':{'net':[3]}
                                      }
                                        }}))
            client.publish(f'/oneM2M/req/{AE_id}/Mobius2/json',
                       json.dumps({'to':containers[1],
                                  'fr':AE_id,
                                  'op':1,
                                  'ty':2,
                                  'rqi':f'{AE_id}_{str(randint(0,100000))}',
                                  'pc':{ 'm2m:sub':{
                                      'rn': 'sub',
                                      'nu': [f'mqtt:/{AE_id}'],
                                      'nct':1,
                                      'enc':{'net':[3]}
                                      }
                                        }}))


def on_data_update(client, userdata, message):
    global last
    print()
    print('New data')
    print(message.topic)
    print(message.payload)
    msg = json.loads(message.payload)
    client.publish('/oneM2M/resp/Mobius2/{AE_id}/json',
                      json.dumps({'to':csi,
                                  'fr':AE_id,
                                  'rqi': msg['rqi'],
                                  'rsc': 2000 })) # rsc: 2xxx request received and done, 1xxx request received but in progress
    idx = msg['pc']['m2m:sgn']['sur'].split('/')[-2]
    last[idx] = float(msg['pc']['m2m:sgn']['nev']['rep']['m2m:cin']['con'])
    data[idx].append(last[idx])


def on_message(client, userdata, message):
    print(message.topic)
    print(message.payload)



global last
# Hardcode for testbed purposes, ideally this would be done with location filters
watch_pair = [('202481601211147','202481586606346'),
              ('','')]

watch_pair = watch_pair[int(sys.argv[2])]
watch_pair = ['_to_'.join(watch_pair), '_to_'.join(watch_pair[::-1])]
data = {watch_pair[0]:[],watch_pair[1]:[]}
last = {watch_pair[0]:.0,watch_pair[1]:.0}


server_address = '10.10.10.114'
csi = 'Mobius'
AE_id = 'RIC-test'+'_'+sys.argv[1]


client = Client()
client.connect(server_address)
client.on_message = on_message

client.subscribe(f'/oneM2M/reg_resp/{AE_id}/Mobius2/+')
client.subscribe(f'/oneM2M/resp/{AE_id}/Mobius2/+')
client.subscribe(f'/oneM2M/req/+/{AE_id}/+')
client.message_callback_add(f'/oneM2M/req/Mobius2/{AE_id}/json',on_data_update)

client.message_callback_add(f'/oneM2M/resp/{AE_id}Init/Mobius2/json',on_ric_discovery)
client.message_callback_add(f'/oneM2M/resp/{AE_id}/Mobius2/json',on_discovery)
client.subscribe(f'/oneM2M/resp/{AE_id}Init/Mobius2/json')
client.subscribe(f'/oneM2M/resp/{AE_id}/Mobius2/json')


client.publish(f'/oneM2M/req/{AE_id}Init/Mobius2/json',
               json.dumps({'to':csi,
                           'fr':AE_id,
                           'rqi':f'{AE_id}_discovery_{str(int(randint(0,100000)))}',
                           'op':2,
                           'fc':{'fu':1,'ty':2}}))
rqi = f'{AE_id}_{str(randint(0,10000))}'
client.publish(f'/oneM2M/req/{AE_id}/Mobius2/json',
               json.dumps({'to':'Mobius/MAORIOT-AE',
                           'fr':AE_id,
                           'rqi':rqi,
                           'op':2,
                           'fc':{'fu':1,'ty':3}}))
sleep(2)


cell_on = False

cell_cin= {'to':'Mobius/{AE_id}/cell_status',
           'fr':AE_id,
           'rqi':str(randint(0,100000)),
           'op':1,
           'ty':4,
           'pc':{'m2m:cin':{'con':cell_on} 
            }
           }
client.publish(f'/oneM2M/req/{AE_id}/Mobius2/json',json.dumps(cell_cin))
client.loop_start()
while(True):
    data[watch_pair[0]] = [x for x in data[watch_pair[0]] if x > last[watch_pair[0]]-60]
    data[watch_pair[1]] = [x for x in data[watch_pair[1]] if x > last[watch_pair[1]]-60]

    print(f'{watch_pair[0]}: {len(data[watch_pair[0]])} devices/min')
    print(f'{watch_pair[1]}: {len(data[watch_pair[1]])} devices/min')

    if len(data[watch_pair[0]])+len(data[watch_pair[1]]) > 1 and not cell_on:
        # Request cell API to turn on
        print('Turning cell off...')
        cell_on = True
        cell_cin['rqi'] = str(randint(0,100000))
        cell_cin['pc']['m2m:cin']['con'] = cell_on
        client.publish(f'/oneM2M/req/{AE_id}/Mobius2/json',json.dumps(cell_cin))
        pass
    elif len(data[watch_pair[0]])+len(data[watch_pair[1]]) <= 0 and cell_on:
        print('Turning cell on...')
        cell_on = False
        cell_cin['rqi'] = str(randint(0,100000))
        cell_cin['pc']['m2m:cin']['con'] = cell_on
        client.publish(f'/oneM2M/req/{AE_id}/Mobius2/json',json.dumps(cell_cin))
        # Request cell API to turn off
        pass
        
    
    last[watch_pair[0]] += 0.1
    last[watch_pair[1]] += 0.1
    print()
    sleep(1)

client.loop_forever()




