import dash
import dash_mantine_components as dmc

dash.register_page(__name__)

layout = dmc.Container([
    dmc.Center([
    dmc.Alert("This Page is currently under construction.")
    ])
])