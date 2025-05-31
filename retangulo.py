import dash
from dash import html, Output, Input, exceptions
import dash_leaflet as dl
import json

# Limites do mapa (alterar se necessário)
max_bounds = [[-20.111472, -44.407691], [-19.530436, -43.613047]]

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
            dl.FeatureGroup([edit_control]) # A ferramenta de desenho
        ],
        style={'height': '100vh'},
        
        # Limitando a região a BH
        maxZoom=18,
        minZoom=12,
        maxBounds=max_bounds,
        maxBoundsViscosity=1.0
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