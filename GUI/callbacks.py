
from components.elements.charts.chart import *
from data.globalVariables import *


def getData():
    global IP
    global PORT
    pass

def update_live_VRgraph(d,value):
    global datVR
    return generateFigLive(datVR,value)

def update_VRdata(n):
    global datVR # Get global variable
    global nIVR

    d = getData() # Get Data from the AEs

    # d should be a dict/json with the following parameters: BTNode_1, BTNode_2, RIC_1 and RIC_2
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