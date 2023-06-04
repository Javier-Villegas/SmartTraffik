from app import *

from paho.mqtt.client import Client
import json
import sys
from time import sleep
from random import randint


def on_discovery(client, userdata, msg):
    print('on discovery')
    print(msg.payload)
    msg_json = json.loads(msg.payload.decode('utf-8'))
    registered = False
    for uri in set(msg_json['pc']['m2m:uril']).difference(subscriptions):
        if ("BTNode" in uri):
            # uri = /Mobius/BTNode_MAC/new_dev
            aux = uri.split("/")
            for x in aux:
                if "BTNode" in x:
                    nodeName = x

            # Create subscription
            mqttc.publish('/oneM2M/req/GUI-test/Mobius2/json',
                          json.dumps(
                              {'to': uri , 'fr': 'GUI-AE', 'rqi': str(randint(0, 10000)), 'op': 1,
                               'ty': 23,
                               'pc': {'m2m:sub': {
                                   'rn': 'Discover_device_gui', 'nu': ["mqtt:/GUI-AE"], 'nct': 1,
                                   'enc': {
                                       'net': [3],
                                   }}}}))
            subscriptions.add(uri)

        elif ("MAORIOT-AE" in uri):
            mqttc.publish('/oneM2M/req/GUI-test/Mobius2/json',
                          json.dumps(
                              {'to': uri, 'fr': 'GUI-AE', 'rqi': str(randint(0, 10000)), 'op': 1,
                               'ty': 23,
                               'pc': {'m2m:sub': {
                                   'rn': 'traffic_pattern_gui', 'nu': ["mqtt:/GUI-AE"], 'nct': 1,
                                   'enc': {
                                       'net': [3],
                                   }}}}))

            subscriptions.add(uri)


def on_gui_discovery(client, userdata, message):
    print()
    print('GUI discovery')
    print(message.topic)
    print(message.payload)
    msg = json.loads(message.payload)
    if msg.get('pc') and msg['pc'].get('m2m:uril'):
        if AE_id not in msg['pc']['m2m:uril']:
            client.publish(f'/oneM2M/reg_req/{AE_id}/Mobius2/json',
                           json.dumps({'to': csi,
                                       'fr': AE_id,
                                       'rqi': AE_id + str(int(randint(0, 10000))),
                                       'op': 1,
                                       'ty': 2,
                                       'pc': {'m2m:ae': {
                                           'rn': AE_id,
                                           'api': 'GUI-Entity',
                                           'rr': True
                                       }}}))
        else:
            print('Reconnecting')


def on_message(client, userdata, message):
    global datVR  # Get global variable
    global nIVR

    print(message.topic)
    print(message.payload)
    msg_json = json.loads(msg.payload.decode('utf-8'))

    if msg_json["pc"].get('m2m:sgn'):
        # Publish ack
        mqttc.publish('/oneM2M/resp/Mobius2/GUI-AE/json',
                      json.dumps({'to': 'Mobius', 'fr': 'GUI-AE', 'rqi': msg_json['rqi'],
                                  'rsc': 2000}))  # rsc: 2xxx request received and done, 1xxx request received but in progress


        # TODO: GET DATA and Plot on GUI
        # Who trigger the notification
        node = msg_json['pc']['m2m:sgn']['nev']['rep']['m2m:cin']['cr']
        if "BTNode" in node:
            # MAC
            mac_address = msg_json['pc']['m2m:sgn']['nev']['rep']['m2m:cin']['con']
            print()
            pass
        elif "MAORIOT-AE" in node:
            subscription_name = msg_json['pc']['m2m:sgn']['sur'] # /Mobius/MAORIOT-AE/<id_path>/<id_subs>
            # Timestamp
            timestamp = msg_json['pc']['m2m:sgn']['nev']['rep']['m2m:cin']['con']
            pass


        # node = re.search(r'(?<=Mobius[/])(\w+)(?=[/]new_dev)', msg_json['to']).group(0)

    d = getData()  # Get Data from the AEs

    # d should be a dict/json with the following parameters: BTNode_1, BTNode_2, RIC_1 and RIC_2
    # if (d != {}):
    #     nIVR = n
    #     now = datetime.now()
    #     d.update({'datetime': now.strftime("%H:%M:%S")})
    #
    #     datVR = datVR.append(d, ignore_index=True)
    #     datVR.reset_index(drop=True, inplace=True)
    #     if (len(datVR) == 20):
    #         datVR = datVR[1:]
    #
    # return nIVR


if __name__ == "__main__":




    server_address = '10.10.10.114'
    csi = 'Mobius'
    AE_id = 'GUI-test'

    client = Client()
    client.connect(server_address)
    client.on_message = on_message

    client.subscribe(f'/oneM2M/reg_resp/{AE_id}/Mobius2/+')
    client.subscribe(f'/oneM2M/resp/{AE_id}/Mobius2/+')
    client.subscribe(f'/oneM2M/req/+/{AE_id}/+')
    client.message_callback_add(f'/oneM2M/req/Mobius2/{AE_id}/json', on_data_update)

    client.message_callback_add(f'/oneM2M/resp/{AE_id}Init/Mobius2/json', on_gui_discovery)
    client.message_callback_add(f'/oneM2M/resp/{AE_id}/Mobius2/json', on_discovery)
    client.subscribe(f'/oneM2M/resp/{AE_id}Init/Mobius2/json')
    client.subscribe(f'/oneM2M/resp/{AE_id}/Mobius2/json')

    client.publish(f'/oneM2M/req/{AE_id}Init/Mobius2/json',
                   json.dumps({'to': csi,
                               'fr': AE_id,
                               'rqi': f'{AE_id}_discovery_{str(int(randint(0, 100000)))}',
                               'op': 2,
                               'fc': {'fu': 1, 'ty': 2}}))
    rqi = f'{AE_id}_{str(randint(0, 10000))}'
    client.publish(f'/oneM2M/req/{AE_id}/Mobius2/json',
                   json.dumps({'to': 'Mobius',
                               'fr': AE_id,
                               'rqi': rqi,
                               'op': 2,
                               'fc': {'fu': 1, 'ty': 3}}))
    sleep(2)

    cell_on = False
    client.loop_start()

    app.run_server(debug=True, host="0.0.0.0", port=8889)

    client.loop_forever()


    #app.run_server(debug=True, host="192.168.196.3", port=8889)
    #app.run_server(debug=True, host="192.168.192.201", port=8889)