import dash_leaflet as dl
import pandas as pd
from dash_extensions.javascript import assign
from dash_extensions.enrich import DashProxy, Input, Output, html, dcc
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Leio os pontos do csv
pontos = pd.read_csv("./dados/bares_restaurantes.csv",sep=';')

# Formatar informações de endereço
pontos["ENDERECO_COMPLETO"] = (pontos["DESC_LOGRADOURO"] + " " + 
                               pontos["NOME_LOGRADOURO"] + ", " + 
                               pontos["NUMERO_IMOVEL"].astype(str) + " " +
                               pontos["COMPLEMENTO"].fillna("") + " - " + 
                               pontos["NOME_BAIRRO"] + ", Belo Horizonte, MG")

# Criar DataFrame formatado
pontos_formatados = pontos[["NOME_FANTASIA", "ENDERECO_COMPLETO", "DATA_INICIO_ATIVIDADE", "IND_POSSUI_ALVARA"]]

#transformo eles em json para poder usar a api com maior eficiencia
#e usar funções que só são possíveis com json
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row['LONGITUDE'], row['LATITUDE']]
            },
            "properties": {"name": str(row['NOME_FANTASIA']),
                            "children": [dl.Tooltip(str(row['NOME_FANTASIA']))]
                           }
        } for _, row in pontos.iterrows() if pd.notna(row['LATITUDE'])
    ]
}


eventHandlers = dict(
    click=assign("function(e, ctx){console.log(`You clicked at ${e.latlng}.`)}"),
)

fig = make_subplots(
    rows=1, cols=1,
    specs=[[{"type": "table"}]]
)

fig.add_trace(
    go.Table(
        header=dict(
            values=["Nome Fantasia", "Endereço", "Início Atividade", "Possui alvará"],
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[
                pontos_formatados["NOME_FANTASIA"].tolist(),
                pontos_formatados["ENDERECO_COMPLETO"].tolist(),
                pontos_formatados["DATA_INICIO_ATIVIDADE"].tolist(),
                pontos_formatados["IND_POSSUI_ALVARA"].tolist()
            ],
            align="left"
        )
    ),
    row=1, col=1
)
#crio o app
app = DashProxy()
app.layout = html.Div(
    [dl.Map(
       [dl.TileLayer(),
        dl.GeoJSON(
                    data=geojson_data,
                    cluster=True,
                    zoomToBoundsOnClick=True,
                    superClusterOptions={"radius": 100},
                )
       ],
       eventHandlers=eventHandlers,
       center=[-19.926214367710706, -43.93821802072859], 
       zoom=10, style={"height": "90vh"},maxZoom=15,
       id = 'map'), 
html.Button("fly to home", id="btn"),
dcc.Graph(
        id='tabela-estabelecimentos',
        figure=fig
    )
    ])

#ponto comum (ícone normal) - 
#ponto mais chamativo 
@app.callback(Output("map", "viewport"), Input("btn", "n_clicks"), prevent_initial_call=True)
def fly_to_home(_):
    return dict(center=[-19.926214367710706, -43.93821802072859], zoom=10, transition="flyTo")

if __name__ == "__main__":
    app.run() # Acessar http://127.0.0.1:8050/
