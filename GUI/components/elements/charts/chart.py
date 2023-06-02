

from dependencies import *

from data.VR_metadata import *


PAR = dict()
PAR_unit = dict()

# VR
PAR.update(VR_tags)

PAR_unit.update(VR_unit)



# CSS
CHART_STYLE = {
    'display': 'auto',
    'text-align':'center',
    'width': '100%',
    'padding': '0px 0px 0px 0px',
    'margin': '0px 0px 0px 0px'
}


def generateFig(value):
    # lab =  LTESTICK[value]["label"]
    try:
        fig = go.Figure()

    except:
        fig = go.Figure()
    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5),
        plot_bgcolor="#FEF9E7",
        #paper_bgcolor = "rgb(254, 249, 231)",
        #yaxis_title=PARAMS_UNIT[value],
        yaxis_title=PAR_unit[value],
        height = 200
    )

    return fig

def chartS(id,menu,initialValue):
    # Plotly Express
    # Metrics is a list with the metrics to show in the dropmenu
    dropMenu = []
    for x in menu:
        #dropMenu.append({'label': x, 'value': x})
        dropMenu.append({'label': VR_tags[x], 'value': x})

    fig = generateFig(initialValue)

    return dbc.Col(html.Div(id=id, children=[
        dcc.Dropdown(id="slct_" + id,
                     options=dropMenu,
                     multi=False,
                     # value=LTESTICK_LABEL_LIST.index(label),
                     value=initialValue,
                     style={'display': 'relative', 'width': "100%", 'text-align': 'center', 'margin-bottom': '0px',"border-color":"#FDEBD0"}
                     ),
        dcc.Graph(id='chart_' + id, figure=fig, config={
            'displayModeBar': False, 'autosizable': True
        }, style={'padding': '0px', 'height': '100%', 'width': "100%", 'text-align': 'center'})
    ], style=CHART_STYLE))





def generateFigLive(d, value):
    if len(d) > 10:
        d = d[-10:]
    try:
        data = d[PAR[value]]
    except:
        data = []

    try:
        fig = go.Figure(data=go.Scatter(x=d['datetime'], y=data, mode="lines+markers",
                                        line_shape='linear', name="Measured",
                        )
        )
    except:

        fig = go.Figure(data=go.Scatter(x=np.arange(len(data)), y=data, mode="lines+markers",
                                        line_shape='linear'))
    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5),
        plot_bgcolor="#FEF9E7",
        yaxis_title=PAR_unit[value],
        height=200
    )


    fig = chartAxis(fig,value)
    return fig

def chartAxis(fig,value):
    if value == "Resolution":
        fig.update_yaxes(categoryarray = ['360p','540p','720p','1080p', '1440p', '4K'],
                         categoryorder = "array", range=[-0.5,6.5])

    elif value == 'averageFPS':
        fig.update_yaxes(range=[69, 76], dtick = 2)

    elif value == 'initPlayingTime' or value == 'stallEvents' or value == 'avgStallTime':
        fig.update_yaxes(rangemode="nonnegative", range = [-0.5, 5])

    elif value == 'stallCount':
        fig.update_yaxes(rangemode="nonnegative")

    return fig
