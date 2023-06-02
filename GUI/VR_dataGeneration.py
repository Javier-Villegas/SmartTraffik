import json
import pandas as pd
import requests
import time
name = "./Log_1631621126.json"


header = {'content-type': 'application/json'}

url = "http://127.0.0.1:6000/data/vr"
i = 0
with open(name, 'r') as file:
    data = json.load(file)


vrD = data['vr']


while(1):
    r = requests.post(url, data=json.dumps(vrD[i]), headers=header)
    i = (i+1)%len(vrD)
    time.sleep(1)
