from dependencies import *

# CSS

# Element
colorLabelNav = "#148F77"
def nav():
    return dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink("Monitoring", active=True, href="/Monitoring")),

        ],
        id = "nav",
        style={'labelColor':colorLabelNav},
        fill = False
    )




