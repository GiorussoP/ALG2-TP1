import dash_leaflet as dl
from dash import Dash

app = Dash()
app.layout = dl.Map(dl.TileLayer(), center=[56, 10], zoom=6, style={"height": "50vh"})

if __name__ == "__main__":
    app.run() # Acessar http://127.0.0.1:8050/
