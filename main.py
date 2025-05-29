import dash_leaflet as dl
import pandas as pd
from dash import Dash
from dash_extensions.enrich import DashProxy, Input, Output, html

pontos = pd.read_csv("./bares_restaurantes.csv",sep=';')

markers = []
for _, row in pontos.iterrows():
    markers.append(
        dl.Marker(
            position=[row['LATITUDE'], row['LONGITUDE']],
            children=[dl.Tooltip(row['NOME_FANTASIA'])],
            draggable=False
        )
    )


app = DashProxy()
app.layout = dl.Map(
       [dl.TileLayer(), 
        *markers
       ],
       center=[-19.926214367710706, -43.93821802072859], 
       zoom=10, style={"height": "90vh"},maxZoom=15,
       id = 'map'), html.Button("fly to home", id="btn"),


#ponto comum (ícone normal) - 
#ponto mais chamativo 
@app.callback(Output("map", "viewport"), Input("btn", "n_clicks"), prevent_initial_call=True)
def fly_to_home(_):
    return dict(center=[-19.926214367710706, -43.93821802072859], zoom=10, transition="flyTo")

if __name__ == "__main__":
    app.run() # Acessar http://127.0.0.1:8050/
