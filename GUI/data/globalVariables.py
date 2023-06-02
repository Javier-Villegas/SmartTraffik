from dependencies import *
# VR
global datVR
global nIVR
datVR = pd.DataFrame()
nIVR = 0
global IP
global PORT
IP = dict()
PORT = dict()


#IP Information of REST Server (not FLASK HTTP SERVER!!!)
IP['rest'] = "127.0.0.1"
#IP['rest'] = "192.168.196.3"
PORT['rest'] = "6000"