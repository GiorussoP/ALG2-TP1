import dash
from dash import html, Output, Input, exceptions, dcc
import pandas as pd
import dash_leaflet as dl
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Limites do mapa (alterar se necessário)
max_bounds = [[-20.111472, -44.407691], [-19.530436, -43.613047]]

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

app = dash.Dash(__name__)

# Ferramenta de desenho que só permite desenhar o retângulo.
edit_control = dl.EditControl(
    id="edit_control",
    position="topleft",
    draw={
        "polyline": False,
        "polygon": False,
        "circle": False,
        "marker": False,
        "circlemarker": False,
        "rectangle": {
            # Estilo do retângulo
            "shapeOptions": {
                "color": "red",
                "weight": 2,
                "opacity": 1.0,
                "fillColor": "orange",
                "fillOpacity": 0.2
            }
        }
    },
    # Para que haja somente 1 retângulo por vez, é necessário ativar a ferramenta de remoção
    edit={"edit": False, "remove": True}
)

app.layout = html.Div([
    dl.Map(
        id="map",
        center=[-19.922746, -43.945142],
        zoom=16,
        children=[
            dl.TileLayer(),
            dl.FeatureGroup([edit_control]), # A ferramenta de desenho
             dl.GeoJSON(
                    data=geojson_data,
                    cluster=True,
                    zoomToBoundsOnClick=True,
                    superClusterOptions={"radius": 100},
                )
        ],
        style={'height': '100vh'},
        
        # Limitando a região a BH
        maxZoom=18,
        minZoom=11,
        maxBounds=max_bounds,
        maxBoundsViscosity=1.0
    ),
    dcc.Graph(
        id='tabela-estabelecimentos',
        figure=fig
    )
])

# Callback ativado quando o desenho do retângulo é finalizado
@app.callback(
    Output("edit_control", "editToolbar"),
    Input("edit_control", "geojson")
)
def pass_rectangle_coordinates(geojson):
    if not geojson:
        raise exceptions.PreventUpdate

    # O retângulo está em uma FeatureCollection
    features = geojson.get("features", [])
    if not features:
        return "Retângulo não desenhado."

    # Obtendo a última forma desenhada
    feature = features[-1]
    geom_type = feature.get("geometry", {}).get("type", "")
    coords = feature.get("geometry", {}).get("coordinates", [])

    # Se existir e estiver corretamente formatado
    if geom_type == "Polygon" and coords:
        
        # Escrevendo as coordenadas (para debug, apenas)
        print("COORDENADAS DO RETANGULO:\n")
        for c in coords:
            for b in c:
                print('\t',b)

        # Removendo todas o retângulo desenhado
        return dict(mode="remove", action="clear all")
    else:
        return "Algo que não é um retângulo foi desenhado."

if __name__ == '__main__':
    app.run(debug=True)