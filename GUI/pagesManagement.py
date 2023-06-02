from dependencies import *
from components.pages.MonitoringVR import monitoringVRComponent

# Function for update page's body from the url
def display_page(pathname):
    #if (pathname == "/monitoring"):
    return monitoringVRComponent()
    #return html.Div([
    #    html.H3("Work in progress")
    #])
