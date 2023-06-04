#####################################################
#                    VR METADATA
#####################################################




VR_tags = dict()
for n in range(1,3):
    VR_tags["BTNode_" + str(n)] = "BT Node " + str(n)

for n in range(1,3):
    VR_tags["Traffic_pattern_" + str(n)] = "Traffic pattern " + str(n)

VR_tags["Cell_status"] = "Cell Status"

VR_unit = dict()
for k in VR_tags.keys():
    if "BTNode" in k != -1:
        VR_unit[k] = "Number of devices"
    elif "Traffic_pattern" in k:
        VR_unit[k] = "Devices/min"
    elif "Cell_status" in k:
        VR_unit[k] = "Cell status"
