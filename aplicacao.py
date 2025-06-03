import dash
from dash import html, Output, Input, exceptions, dcc
import pandas as pd
import dash_leaflet as dl
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots


from _2d_tree import node, _2d_tree
from tree_csv_aux_functions import build_aux_structures, format_results


data_path = "./dados/bares_restaurantes.csv"

# Montando 2d tree
data_vector = []
points = []
points, data_vector = build_aux_structures(data_path)
tree = _2d_tree()
tree.build(points)
print("Pontos na 2d-tree:",tree.__len__())





# Limites do mapa (alterar se necessário)
max_bounds = [[-20.029366, -44.067056], [-19.761008, -43.853582]]

#Leio os pontos do csv
pontos = pd.read_csv(data_path,sep=';')

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
     html.Div(dcc.Graph(
        id='tabela-estabelecimentos',
        figure=fig
    ), 
    style={
                'flex': '1',        
                'maxWidth': '100%',  
                'overflowY': 'auto',
                'padding': '10px'
        }
    ),
    html.Div(dl.Map(
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
                        superClusterOptions={"radius": 200},
                    )
            ],
            style={'height': '100vh'},
            
            # Limitando a região a BH
            maxZoom=20,
            minZoom=12,
            maxBounds=max_bounds,
            maxBoundsViscosity=1.0
        ),
        style={
                'flex': '2',
                'padding': '10px'
        }
    )
    ],
    style={
        'display': 'flex',
        'height': '100vh'
    }

)

# Callback ativado quando o desenho do retângulo é finalizado
@app.callback(
    Output("tabela-estabelecimentos", "figure"),
    Output("edit_control", "editToolbar"),
    Input("edit_control", "geojson")
)
def update_table_via_tree(geojson):
    # Se não houver geojson, não atualiza nada.
    if not geojson:
        raise exceptions.PreventUpdate

    # Se não houver features, não atualiza nada.
    features = geojson.get("features", [])
    if not features:
        return dash.no_update, dash.no_update

    # Buscando a última forma desenhada (o retângulo).
    feature = features[-1]
    geom = feature.get("geometry", {})
    geom_type = geom.get("type", "")
    coords = geom.get("coordinates", [])

    # Caso não seja um polígono ou não tenha coordenadas, não atualiza nada.
    if geom_type != "Polygon" or not coords:
        return dash.no_update, dash.no_update

    min_lon, min_lat = coords[0][0]
    max_lon, max_lat = coords[0][2]

    # Usando a 2d-tree para buscar os pontos dentro do retângulo.
    results = tree.range_search((min_lat, max_lat, min_lon, max_lon))
    print("Tree search results:", results)

    # Filtrando o DataFrame com base nos IDs encontrados.
    id_list = [node.ID for node in results]
    print("ID list extracted:", id_list)
    filtered_df = pontos_formatados.iloc[id_list]

    # Criando tabela com os dados filtrados.
    new_fig = make_subplots(rows=1, cols=1, specs=[[{"type": "table"}]])
    new_fig.add_trace(
        go.Table(
            header=dict(
                values=["Nome Fantasia", "Endereço", "Início Atividade", "Possui alvará"],
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=[
                    filtered_df["NOME_FANTASIA"].tolist(),
                    filtered_df["ENDERECO_COMPLETO"].tolist(),
                    filtered_df["DATA_INICIO_ATIVIDADE"].tolist(),
                    filtered_df["IND_POSSUI_ALVARA"].tolist()
                ],
                align="left"
            )
        ),
        row=1, col=1
    )

    # Atualizando tabela e limpando o retângulo desenhado.
    return new_fig, dict(mode="remove", action="clear all")
if __name__ == '__main__':
    app.run(debug=True)
