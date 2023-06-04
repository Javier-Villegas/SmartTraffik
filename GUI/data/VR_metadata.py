#####################################################
#                    VR METADATA
#####################################################

global nVIR



ndev = {"BTNode202481601211147":0, "BTNode202481586606346":0, "202481601211147_to_202481586606346":0,"202481586606346_to_202481601211147":0}



VR_tags = dict()
# for n in range(1,3):
#     VR_tags["BTNode_" + str(n)] = "BT Node " + str(n)

count = 0
print(ndev)
for n in ndev.keys():
    VR_tags[n] = "BT Node " + str(count)
    count +=1

VR_tags["202481601211147_to_202481586606346"] = "Traffic pattern 1"
VR_tags["202481586606346_to_202481601211147"] = "Traffic pattern 2"

VR_tags["Cell_status"] = "Cell Status"

VR_unit = dict()
for k in VR_tags.keys():
    if "BTNode" in k != -1:
        VR_unit[k] = "Number of devices"
    elif "to" in k:
        VR_unit[k] = "Devices/min"
    elif "Cell_status" in k:
        VR_unit[k] = "Cell status"
