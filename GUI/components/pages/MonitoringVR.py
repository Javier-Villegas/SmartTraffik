
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
                chartS(id = "_f1", menu = dropMenuCharts, initialValue = "BTNode202481601211147"),
                chartS(id = "_f2", menu = dropMenuCharts, initialValue = "BTNode202481601211147")
            ]
             ),

    dbc.Row(
            [
                chartS(id = "_f3",menu = dropMenuCharts, initialValue = "202481601211147_to_202481586606346"),
                chartS(id = "_f4",menu = dropMenuCharts, initialValue = "202481586606346_to_202481601211147"),

            ]
            ),

    dbc.Row(
            [
                chartS(id = "_f5", menu = dropMenuCharts, initialValue = "Cell_status"),
            ]
            )


    ],
    style =  contentStyle
)





def monitoringVRComponent():
    component = html.Div(id= "measuresComponentVR" ,children = [
        content
    ],
                         style = {'width': "100%"})
    return component

