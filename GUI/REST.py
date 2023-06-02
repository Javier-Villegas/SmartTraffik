import json

import pandas as pd

from dependencies import *


# Variables



global unreadValue
global dataBuff
global config

unreadValue = dict()
dataBuff = dict()
config = list()




res = {'360':'360p','540':'540p','720':'720p', '1080':'1080p', '1440': '1440p', '1920':'4K'}

global dA
dA = dict()


dA['vr'] = pd.DataFrame()
unreadValue['vr'] = False

if __name__=='__main__':
    app = Flask(__name__)
    api = Api(app)

    class info(Resource):
        def get(self,req):
            #TODO
            if (req == "elements"): # Return information about the elements which are posting data
                global data
                return data.keys()


    class data(Resource):
        def get(self,element): # Get the data posted by one element
            global unreadValue
            global dA
            # Return all element values
            if (element == "all"):
                for e in unreadValue:
                    if (not e):
                        break #If there is one element to false, exit from the loop
                if (e):
                    auxD = dict()
                    for d in dA.keys():
                        auxD.update(dA[d].iloc[-1].to_json())

                    return json.loads(auxD)

                else: # If there is an element which has not been updated, nothing is returned
                    return {}, 200
            elif(element == "allD"):
                return json.loads(dA['service'].to_json())
            # Nonetheless, it corresponds with only one value

            else:
                print(unreadValue[element])
                if unreadValue[element]: # Check there is new data to return
                    unreadValue[element] = False # Set the value as readed
                    return json.loads(dA[element].iloc[-1].to_json())
                else: # Nothing is returned if there isn't new data
                    return {}, 200

        def post(self,element):
            try:
                jd = request.get_json()
            except:
                return "Data isn't in the correct format", 400
            try:
                global unreadValue
                unreadValue[element] = True # Set there is new data for this element


                if element == "vr":
                    jd = jd["Items"][0]

                aux = pd.DataFrame.from_records([jd])
                print(aux)
                if element == "vr":
                    try:
                        aux['Resolution'] = res[str(aux['videoHeight'].iloc[0])]
                    except:
                        aux['Resolution'] = str(aux['videoHeight'].iloc[0])
                global dA
                dA[element] = pd.concat([dA[element], aux], ignore_index=True) #Update dataset
                return 200
            except:
                traceback.print_exc()
                return "Something wrong at saving data", 500






    api.add_resource(info,"/info/<string:req>")
    api.add_resource(data, "/data/<string:element>")

    app.run(host="0.0.0.0", port = 6000)