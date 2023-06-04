from callbacks import *
from components.elements.menus.menu_nav import *
from pagesManagement import *
import dash_daq as daq

from data.globalVariables import *
#from app import *
from paho.mqtt.client import Client
import json
import sys
from time import sleep
from random import randint
subscriptions = set()

global ndev
ndev = {}


def update_live_VRgraph(d,value):
    global datVR
    return generateFigLive(datVR,value)

def update_VRdata(n):
    global nIVR
    print("nIVR:" + str(nIVR))
    return nIVR

# Update timer interval
def updateInterval(value):
    global tInterval #Global variable for timerInterval

    tInterval = 1000 * value
    return tInterval

def on_discovery(client, userdata, msg):

    global ndev
    print('on discovery')

    msg_json = json.loads(msg.payload.decode('utf-8'))


    print(msg_json)
    if "pc" in msg_json and "m2m:uril" in msg_json["pc"]:
        print("Discover message")
        for uri in set(msg_json['pc']['m2m:uril']).difference(subscriptions):
            if ("BTNode" in uri):
                # uri = /Mobius/BTNode_MAC/new_dev
                aux = uri.split("/")
                for x in aux:
                    if "BTNode" in x:
                        nodeName = x
                        print(x)
                        ndev[x] = 0


                # Create subscription
                client.publish('/oneM2M/req/GUI-test/Mobius2/json',
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
                client.publish('/oneM2M/req/GUI-test/Mobius2/json',
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
    global ndev

    print(message.topic)
    print(message.payload)
    msg_json = json.loads(message.payload.decode('utf-8'))
    if msg_json["pc"].get('m2m:sgn'):
        # Publish ack
        client.publish('/oneM2M/resp/Mobius2/GUI-AE/json',
                      json.dumps({'to': 'Mobius', 'fr': 'GUI-AE', 'rqi': msg_json['rqi'],
                                  'rsc': 2000}))  # rsc: 2xxx request received and done, 1xxx request received but in progress


        # TODO: GET DATA and Plot on GUI
        # Who trigger the notification
        node = msg_json['pc']['m2m:sgn']['nev']['rep']['m2m:cin']['cr']

        print("DATA from " + node)
        if "BTNode" in node:
            # MAC
            sur = msg_json['pc']['m2m:sgn']['sur']

            btnode = sur.split("/")[1]

            if "new_dev" in sur:
                ndev[btnode] += 1
            elif "del_dev" in sur:
                ndev[btnode] -= 1

            print(ndev[btnode])
            #mac_address = msg_json['pc']['m2m:sgn']['nev']['rep']['m2m:cin']['con']

        elif "MAORIOT-AE" in node:
            sur = msg_json['pc']['m2m:sgn']['sur'] # /Mobius/MAORIOT-AE/<id_path>/<id_subs>


            # Timestamp
            timestamp = msg_json['pc']['m2m:sgn']['nev']['rep']['m2m:cin']['con']
            ndev[sur] = timestamp



        # node = re.search(r'(?<=Mobius[/])(\w+)(?=[/]new_dev)', msg_json['to']).group(0)



    # d should be a dict/json with the following parameters: BTNode_1, BTNode_2, RIC_1 and RIC_2

        nIVR = nIVR +1
        print("nivr in on_message: " + str(nIVR) )
        now = datetime.now()
        d = ndev
        d.update({'datetime': now.strftime("%H:%M:%S")})
        global datVR
        datVR = datVR.append(d, ignore_index=True)
        datVR.reset_index(drop=True, inplace=True)
        if (len(datVR) == 20):
            datVR = datVR[1:]

    return nIVR








server_address = '10.10.10.114'
csi = 'Mobius'
AE_id = 'GUI-test'
    

    
client = Client()
client.connect(server_address)
client.on_message = on_message

client.subscribe(f'/oneM2M/reg_resp/{AE_id}/Mobius2/+')
client.subscribe(f'/oneM2M/resp/{AE_id}/Mobius2/+')
client.subscribe(f'/oneM2M/req/+/{AE_id}/+')
client.subscribe('/oneM2M/req/+/GUI-AE/+')
client.message_callback_add(f'/oneM2M/req/Mobius2/{AE_id}/json', on_message)

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





app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

    # PAGE CONTENT STYLE (CSS)
PAGE_CONTENT = {
        # "clear": "both",
        "padding": "0px",
        # "background-color": "#f8f9fa",
        "background-color": "#FDFEFE"
    }

    # APP LAYOUT
app.layout = dbc.Container([
        dcc.Location(id='url', refresh=False),

        # Timers
        dcc.Interval(
            id='timerVR',
            interval=2 * 1000,  # in milliseconds
            n_intervals=0
        ),

        html.Div([
            dbc.Row(
                [
                    dbc.Col(nav()),
                    dbc.Col(),
                    dbc.Col("Interval: ", align="end", width="auto"),
                    dbc.Col(
                        daq.Slider(
                            id='refreshTime',
                            min=1,
                            max=10,
                            step=1,
                            value=2,
                            marks={
                                2: '2',
                                4: '4',
                                6: '6',
                                8: '8',
                                10: '10'
                            },
                            size=300
                        ),
                        align="center"
                    ),

                ],
                justify="end"
                # style={'display': 'inline-block', 'horizontal-align': 'left', 'margin-left': '0vw', 'margin-top': '0vw'}
            )
        ]
            # style={'display': 'inline-block', 'horizontal-align': 'left', 'margin-left': '0vw', 'margin-top': '0vw'}
        ),

        html.Hr(),
        html.Div(id="page-content", style=PAGE_CONTENT),
        html.Hr(),

        # html.Div([
        #     # html.Img(src='data:image/png;base64,{}'.format(encoded_image))
        #    html.Img(src=("./assets/mobilenet.png"), width="200px", style={"margin-left": "30px"}),
        #    html.Img(src=("./assets/Telma.png"), width="200px", style={"margin-left": "30px"}),
        #    html.Img(src=("./assets/uma.png"), width="100px", style={"margin-left": "30px"}),
        #    html.Img(src=("./assets/vodafone.png"), width="100px", style={"margin-left": "30px"}),
        #    html.Img(src=("./assets/juntaAndalucia.svg"), width="130px", style={"margin-left": "30px"}),
        #    html.Img(src=("./assets/UE.svg"), width="130px", style={"margin-left": "30px"}),
        #    html.Img(src=("./assets/andalucia_UE.svg"), width="130px", style={"margin-left": "30px"}),
        #
        # ], style={'text-align': "centering"}),
        # Hidden variables
        html.Div(id="varVRData", style={'display': 'none'}),

    ])

    ###################################################################################################
    #                                       CALLBACKS Definitions
    ###################################################################################################

    # Page management
app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])(display_page)

    # VR chart update
for graph in range(1, 5):
    app.callback(Output('chart_f' + str(graph), 'figure'),
                    Input('varVRData', 'children'),

                     Input('slct_f' + str(graph), 'value'),
                 Input("timerVR", "n_intervals")
                     )(update_live_VRgraph)

    ## update vr data
app.callback(Output('varVRData', 'children'),
                 Input('timerVR', 'n_intervals')
                 )(update_VRdata)

    # Callback for slider value-changing
app.callback(Output('timerVR', 'interval'),
                 Input('refreshTime', 'value')
                 )(updateInterval)
    #app.run_server(debug=True, host="192.168.196.3", port=8889)
    #app.run_server(debug=True, host="192.168.192.201", port=8889)
app.run_server(debug=True, host="0.0.0.0", port=8889)

client.loop_forever()