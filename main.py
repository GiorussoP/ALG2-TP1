import dash_leaflet as dl
from dash import Dash
from dash_extensions.enrich import DashProxy, Input, Output, html

app = DashProxy()
app.layout = dl.Map(
       [dl.TileLayer(), 
        dl.Marker(position=[55, 10])
       ],
       center=[-19.926214367710706, -43.93821802072859], 
       zoom=10, style={"height": "60vh"},
       id = 'map'), html.Button("fly to home", id="btn"),


#ponto comum (ícone normal) - 
#ponto mais chamativo 
@app.callback(Output("map", "viewport"), Input("btn", "n_clicks"), prevent_initial_call=True)
def fly_to_home(_):
    return dict(center=[-19.926214367710706, -43.93821802072859], zoom=10, transition="flyTo")

if __name__ == "__main__":
    app.run() # Acessar http://127.0.0.1:8050/
