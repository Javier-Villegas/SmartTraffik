from callbacks import *
from components.elements.menus.menu_nav import *
from pagesManagement import *
import dash_daq as daq


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# PAGE CONTENT STYLE (CSS)
PAGE_CONTENT = {
    # "clear": "both",
    "padding": "0px",
    #"background-color": "#f8f9fa",
    "background-color": "#FDFEFE"
}

# APP LAYOUT
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),

    # Timers
    dcc.Interval(
        id='timerVR',
        interval=2 * 1000,  # in milliseconds
        n_intervals=0
    ),


    html.Div([
        dbc.Row(
            [
                dbc.Col(nav()),
                dbc.Col(),
                dbc.Col("Interval: ", align = "end", width = "auto"),
                dbc.Col(
                    daq.Slider(
                        id='refreshTime',
                        min=1,
                        max=10,
                        step=1,
                        value=2,
                        marks={
                            2: '2',
                            4: '4',
                            6: '6',
                            8: '8',
                            10: '10'
                        },
                        size=300
                    ),
                    align = "center"
                ),

            ],
            justify = "end"
        #style={'display': 'inline-block', 'horizontal-align': 'left', 'margin-left': '0vw', 'margin-top': '0vw'}
        )
        ]
        #style={'display': 'inline-block', 'horizontal-align': 'left', 'margin-left': '0vw', 'margin-top': '0vw'}
    ),

    html.Hr(),
    html.Div(id = "page-content", style = PAGE_CONTENT),
    html.Hr(),

    #html.Div([
    #     # html.Img(src='data:image/png;base64,{}'.format(encoded_image))
    #    html.Img(src=("./assets/mobilenet.png"), width="200px", style={"margin-left": "30px"}),
    #    html.Img(src=("./assets/Telma.png"), width="200px", style={"margin-left": "30px"}),
    #    html.Img(src=("./assets/uma.png"), width="100px", style={"margin-left": "30px"}),
    #    html.Img(src=("./assets/vodafone.png"), width="100px", style={"margin-left": "30px"}),
    #    html.Img(src=("./assets/juntaAndalucia.svg"), width="130px", style={"margin-left": "30px"}),
    #    html.Img(src=("./assets/UE.svg"), width="130px", style={"margin-left": "30px"}),
    #    html.Img(src=("./assets/andalucia_UE.svg"), width="130px", style={"margin-left": "30px"}),
    #
    # ], style={'text-align': "centering"}),
    # Hidden variables
    html.Div(id="varVRData", style={'display': 'none'}),

])

###################################################################################################
#                                       CALLBACKS Definitions
###################################################################################################

# Page management
app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])(display_page)

# VR chart update
for graph in range(1,5):
    app.callback(Output('chart_f' + str(graph),'figure'),
                 Input('varVRData', 'children'),

                 Input('slct_vr_f' + str(graph), 'value')
                 )(update_live_VRgraph)

## update vr data
app.callback(Output('varVRData', 'children'),
             Input('timerVR', 'n_intervals')
             )(update_VRdata)



# Callback for slider value-changing
app.callback(Output('timerVR', 'interval'),
             Input('refreshTime', 'value')
             )(updateInterval)
