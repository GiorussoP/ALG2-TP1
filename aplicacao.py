import dash
from dash import html, Output, Input, exceptions, dcc
import pandas as pd
import dash_leaflet as dl
import csv
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash_extensions.javascript import assign



from _2d_tree import node, _2d_tree

#caminho do csv
data_path = "./dados/bares_restaurantes.csv"


# Limites do mapa (alterar se necessário)
max_bounds = [[-20.029366, -44.067056], [-19.761008, -43.853582]]

#Leio os pontos do csv
pontos = pd.read_csv(data_path,sep=';')

# Formatar informações de endereço
pontos["ENDERECO_COMPLETO"] = (pontos["DESC_LOGRADOURO"] + " " + 
                               pontos["NOME_LOGRADOURO"] + ", " + 
                               pontos["NUMERO_IMOVEL"].astype(str) + " " +
                               pontos["COMPLEMENTO"].fillna("") + " - " + 
                               pontos["NOME_BAIRRO"] + ", Belo Horizonte, MG").str.title()

# Criar DataFrame formatado
pontos_formatados = pontos[["ENDERECO_COMPLETO", "DATA_INICIO_ATIVIDADE", "IND_POSSUI_ALVARA"]]

#formatando as linhas para um tipo Title
for col in pontos_formatados.select_dtypes(include=['object']):
    pontos_formatados[col] = pontos_formatados[col].str.title()


#colocando o nome fantasia nos pontos, caso não possua, vai no nome cadastrado
pontos["NOME_FANTASIA"] = pontos["NOME_FANTASIA"].fillna(pontos["NOME"]).copy().str.title()
pontos_formatados["NOME_FANTASIA"] = pontos["NOME_FANTASIA"]


#vetor de pontos
points = []
#transformo eles em json para poder usar a api com maior eficiencia
#e usar funções que só são possíveis com json
geojson_data = {
    "type": "FeatureCollection",
    "features": [
            (
            points.append(
                node(
                    ID=idx,
                    lat=(float(row["LATITUDE"])),
                    lon=(float(row["LONGITUDE"]))
                )
            ),           
            {  # Retorna o GeoJSON Feature
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row['LONGITUDE'], row['LATITUDE']]
                },
                "properties": {
                    "name": str(row['NOME_FANTASIA']),
                    "children": [dl.Tooltip(str(row['NOME_FANTASIA']))]
                }
            }
        )[1]  # Pega apenas o segundo elemento (o GeoJSON Feature)
        for idx, row in pontos.iterrows()
        if pd.notna(row['LATITUDE'])  # Filtra coordenadas válidas
    ]
}

#montando arvore 2d
tree = _2d_tree()
tree.build(points)
print("Pontos na 2d-tree:",tree.__len__())

#montando o subplot da tabela
fig = make_subplots(
    rows=1, cols=1,
    specs=[[{"type": "table"}]],
)

#montando a tabela
fig.add_trace(
    go.Table(
        header=dict(
            values=[
                "<b>Nome</b>",
                "<b>Endereço</b>",
                "<b>Início da Atividade</b>",
                "<b>Possui alvará?</b>"
            ],
            font=dict(color='black', size=14),
            fill_color='#FF7B39',
            align="center",
            height=60,
            line=dict(color="#A4020C", width=4)
        ),
        cells=dict(
            values=[
                pontos_formatados["NOME_FANTASIA"].tolist(),
                pontos_formatados["ENDERECO_COMPLETO"].tolist(),
                pontos_formatados["DATA_INICIO_ATIVIDADE"].tolist(),
                pontos_formatados["IND_POSSUI_ALVARA"].tolist()
            ],
            font=dict(color='white', size=12),
            fill_color='#A62C00',  
            align="left",
            height=50,
            line=dict(color="#A6000E", width=2)
        )
    ),
    row=1, col=1
)
fig.update_layout(
    paper_bgcolor='#A6000E',
    plot_bgcolor='#A6000E',
    margin=dict(l=0, r=0, t=0, b=0)
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
                "fillColor": "#FF7B39",
                "fillOpacity": 0.2
            }
        }
    },
    # Para que haja somente 1 retângulo por vez, é necessário ativar a ferramenta de remoção
    edit={"edit": False, "remove": True}
)

#atualizando o espaçamento da tabela na div do navegador
fig.update_layout(
    margin=dict(l=0, r=0, t=2, b=0),
    height=None
)
app.layout = html.Div([
            html.Div([
                html.H3(
                    "DESENHE UM RETÂNGULO PARA FILTRAR BARES E RESTAURANTES:",
                    style={"textAlign": "center", "color": "white", "padding": "10px","fontFamily": "Helvetica"}
                ),
                html.Div(
                    dcc.Graph(
                        id='tabela-estabelecimentos',
                        figure=fig,
                        config={'displayModeBar': False},
                        style={
                            'height': '100vh'
                        }
                    ),
                    style={
                        'flex': '1'
                    }
                )
            ], 
            style={
                "display": "flex", 
                "flexDirection": "column",
                'flex': '1',          
                'maxWidth': '100%',
                'overflowY': 'auto',    
                'height': '100vh',
                'width': '100%',        
                'align': 'center',
                'margin' : '0',
            }
        ),
        html.Div(dl.Map(
                id="map",
                center=[-19.922746, -43.945142],
                zoom=16,
                children=[
                    dl.TileLayer(
                        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                    ),
                    dl.FeatureGroup([edit_control]), # A ferramenta de desenho
                    dl.GeoJSON(
                            data=geojson_data,
                            cluster=True,
                            zoomToBoundsOnClick=True,
                            superClusterOptions={"radius": 100},
                            pointToLayer=assign("""
                                function(feature, latlng) {
                                    var marker = L.marker(latlng);
                                    if (feature.properties && feature.properties.name) {
                                        marker.bindTooltip(feature.properties.name, {direction: 'top'});
                                    }
                                    return marker;
                                }
                            """)
                        )
                ],
                style={'height': '100vh'},
                
                # Limitando a região a BH
                maxZoom=18,
                minZoom=12,
                maxBounds=max_bounds,
                maxBoundsViscosity=1.0
            ),
            style={
                    'flex': '3'
            }
        )
    ],
    style={
        'display': 'flex',
        'height': '100vh',
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
    #print("Tree search results:", results)

    # Filtrando o DataFrame com base nos IDs encontrados.
    id_list = [node.ID for node in results]
    #print("ID list extracted:", id_list)
    filtered_df = pontos_formatados.iloc[id_list]

    # Criando tabela com os dados filtrados.
    new_fig = make_subplots(rows=1, cols=1, specs=[[{"type": "table"}]])
    new_fig.add_trace(
        go.Table(
        header=dict(
            values=[
                "<b>Nome</b>",
                "<b>Endereço</b>",
                "<b>Início da Atividade</b>",
                "<b>Possui alvará?</b>"
            ],
            font=dict(color='black', size=14),
            fill_color='#FF7B39',
            align="center",
            height=60,
            line=dict(color="#A4020C", width=4)
        ),
        cells=dict(
            values=[
                filtered_df["NOME_FANTASIA"].tolist(),
                filtered_df["ENDERECO_COMPLETO"].tolist(),
                filtered_df["DATA_INICIO_ATIVIDADE"].tolist(),
                filtered_df["IND_POSSUI_ALVARA"].tolist()
            ],
            font=dict(color='white', size=12),
            fill_color='#A62C00',
            align="left",
            height=50,
            line=dict(color="#A6000E", width=2)
        )
    ),
    row=1, col=1
    )

    new_fig.update_layout(
        paper_bgcolor='#A6000E',
        plot_bgcolor='#A6000E',
        margin=dict(l=0, r=0, t=2, b=0),
        height=None
    )

    # Atualizando tabela e limpando o retângulo desenhado.
    return new_fig, dict(mode="remove", action="clear all")
if __name__ == '__main__':
    app.run(debug=True)
