
from components.elements.charts.chart import *


#CSS

contentStyle = {"display": "inline-block", "padding": "0px 0px 0px 0px", "padding-top":"10px", "width": "100%"}


########################################
#           Component's content
########################################


dropMenuCharts = list(VR_tags.keys())




content = html.Div(id = "measuresContent", children = [

    dbc.Row(
            [
                chartS(id = "chart_f1", menu = dropMenuCharts, initialValue = "BTNode_1"),
                chartS(id = "chart_f2", menu = dropMenuCharts, initialValue = "BTNode_2"),
                chartS(id = "chart_f3", menu = dropMenuCharts, initialValue = "RIC_1"),
            ]
             ),

    dbc.Row(
            [
                chartS(id = "chart_f4",menu = dropMenuCharts, initialValue = "BTNode_3"),
                chartS(id = "chart_f5",menu = dropMenuCharts, initialValue = "BTNode_4"),
                chartS(id = "chart_f6", menu = dropMenuCharts, initialValue = "RIC_2"),
            ]
            ),


    ],
    style =  contentStyle
)





def monitoringVRComponent():
    component = html.Div(id= "measuresComponentVR" ,children = [
        content
    ],
                         style = {'width': "100%"})
    return component
