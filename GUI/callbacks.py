
from components.elements.charts.chart import *
from data.globalVariables import *


def getDataVR():
    global IP
    global PORT
    base = "http://" + IP['rest'] + ":" + PORT['rest']
    header = {'content-type': 'application/json'}
    url = "/data/vr"
    d = dict()

    try:
        r = requests.get(base + url, timeout=10, headers=header)
        return r.json()
    except:
        traceback.print_exc()
        print("REST unavailable")
        try:
            print("Second intent")
            r = requests.get(base + url, timeout=10, headers=header)
            return r.json()
        except:
            print("Something wrong")
            return {}

def update_live_VRgraph(d,value):
    global datVR
    return generateFigLive(datVR,value)

def update_VRdata(n):
    global datVR # Get global variable
    global nIVR

    d = getDataVR() # Get Data from the REST
    if (d != {}):
        nIVR = n
        now = datetime.now()
        d.update({'datetime': now.strftime("%H:%M:%S")})

        datVR = datVR.append(d, ignore_index=True)
        datVR.reset_index(drop=True, inplace=True)
        if(len(datVR) == 20):
            datVR = datVR[1:]


    return nIVR

# Update timer interval
def updateInterval(value):
    global tInterval #Global variable for timerInterval

    tInterval = 1000 * value
    return tInterval