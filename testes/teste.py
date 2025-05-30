import folium
from flask import Flask, send_file
from folium.plugins import MarkerCluster
import pandas as pd
import threading

# 1. Carregar dados com tratamento de erros
try:
    pontos = pd.read_csv("./bares_restaurantes.csv", sep=';')
    
    # Verificar colunas necessárias
    required_cols = {'LATITUDE', 'LONGITUDE', 'NOME_FANTASIA'}
    if not required_cols.issubset(pontos.columns):
        missing = required_cols - set(pontos.columns)
        raise ValueError(f"Colunas faltando: {missing}")

except Exception as e:
    print(f"Erro ao carregar dados: {e}")
    exit()

# 2. Limpar dados - remover linhas com coordenadas inválidas
pontos_clean = pontos.dropna(subset=['LATITUDE', 'LONGITUDE']).copy()

# Converter para numérico e filtrar coordenadas válidas
pontos_clean['LATITUDE'] = pd.to_numeric(pontos_clean['LATITUDE'], errors='coerce')
pontos_clean['LONGITUDE'] = pd.to_numeric(pontos_clean['LONGITUDE'], errors='coerce')
pontos_clean = pontos_clean.dropna(subset=['LATITUDE', 'LONGITUDE'])
pontos_clean = pontos_clean[
    (pontos_clean['LATITUDE'].between(-90, 90)) & 
    (pontos_clean['LONGITUDE'].between(-180, 180))
]

print(f"Total de pontos válidos: {len(pontos_clean)}/{len(pontos)}")

# 3. Criar mapa
m = folium.Map(
    location=[-19.926214367710706, -43.93821802072859],
    zoom_start=12,
    tiles='OpenStreetMap'
)

# 4. Adicionar cluster
marker_cluster = MarkerCluster().add_to(m)

# 5. Adicionar marcadores
for _, row in pontos_clean.iterrows():
    popup = str(row['NOME_FANTASIA']) if pd.notna(row['NOME_FANTASIA']) else "Sem nome"
    
    folium.Marker(
        location=[row['LATITUDE'], row['LONGITUDE']],
        popup=popup,
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(marker_cluster)

# 6. Salvar e abrir
output_file = 'mapa_cluster.html'
m.save(output_file)
print(f"Mapa salvo como {output_file}")

# Criar servidor Flask
app = Flask(__name__)

@app.route('/')
def show_map():
    return send_file('mapa_cluster.html')

def run_server():
    app.run(host='0.0.0.0', port=8050)

if __name__ == '__main__':
    print("Servidor iniciado em http://localhost:8050")
    threading.Thread(target=run_server).start()
    
    # Opcional: abrir navegador automaticamente
    import webbrowser
    webbrowser.open('http://localhost:8050')
