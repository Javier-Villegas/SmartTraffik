
from components.elements.charts.chart import *
#from data.globalVariables import *




def update_live_VRgraph(d,value,s):
    global datVR
    print("datVR:")
    print(datVR)
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