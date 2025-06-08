import csv
from _2d_tree import node, _2d_tree


def truncate(number, decimals=6):
    factor = 10 ** decimals
    return int(number * factor) / factor

def build_aux_structures(path):
    #retorna (dados no formato para build_tree, vetor dos dados detalhados com index correspondente ao id do tipo node)
    data_vector = []
    points = []

    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for idx, row in enumerate(reader):        
            nome = row["NOME"]
            nome_fantasia = row["NOME_FANTASIA"]
            logradouro = row["DESC_LOGRADOURO"]
            nome_logradouro = row["NOME_LOGRADOURO"]
            numero = row["NUMERO_IMOVEL"]
            bairro = row["NOME_BAIRRO"]
            possui_alvara = row["IND_POSSUI_ALVARA"]
            data_inicio = row["DATA_INICIO_ATIVIDADE"]
            latitude = truncate(float(row["LATITUDE"]))
            longitude = truncate(float(row["LONGITUDE"]))

            address = f"{logradouro} {nome_logradouro} {numero} {bairro}".strip()

            data_vector.append((nome, nome_fantasia, address, possui_alvara, data_inicio))

            pt = node(ID=idx, lat=latitude, lon=longitude)
            points.append(pt)
    return (points, data_vector)

def format_results(results, dict):
    formated_result = []
    for result in results:
        formated_result = dict[result.ID] 
    return formated_result