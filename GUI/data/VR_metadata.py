#####################################################
#                    VR METADATA
#####################################################




VR_tags = dict()
for n in range(1,5):
    VR_tags["BTNode_" + str(n)] = "BT Node " + str(n)

for n in range(1,3):
    VR_tags["RIC_" + str(n)] = "Network cell " + str(n)

VR_unit = dict()
for k in VR_tags.keys():
    if k.find("BTNode") != -1:
        VR_unit[k] = "Devices/min"
    elif k.find("RIC") != -1:
        VR_unit[k] = "Cell status"
