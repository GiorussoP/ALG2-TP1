import csv
import json
import re
import unicodedata

'''
Dados do json tratados (erros simples como typos de nomes e inconsistencia de bairros) manualmente para o cruzamento dos dados:
    Rua Dona Geni, 32 | Jardim Florência (Venda Nova), Belo Horizonte  para  Rua Dona Geni, 32 | Maria Helena, Belo Horizonte
    Rua Piauí, 1884 | Funcionários, Belo Horizonte  para  Rua Piauí, 1884 | Savassi, Belo Horizonte
    RUA VICENTINA COUTINHO CAMARGOS, 100, BELO HORIZONTE  para  RUA VICENTINA COUTINHO CAMARGOS, 100 | Alvaro Camargos, BELO HORIZONTE
    Rua Java, 386 | Nova Suíça, Belo Horizonte  para  Rua Java, 386 | Nova Suissa, Belo Horizonte
    Rua Pirite, 187 | Santa Teresa, Belo Horizonte  para  Rua Pirite, 187 | Santa Tereza, Belo Horizonte
    Rua Tamoios, 232 | Centro, Belo Horizonte  para  Rua dos Tamoios, 232 | Centro, Belo Horizonte
    Rua Coronel José Benjamim, 770 | Padre Eustáquio, Belo Horizonte  para  Avenida Coronel José Benjamim, 770 | Padre Eustáquio, Belo Horizonte
    Avenida Vicente Risola, 1305 | Santa Inês, Belo Horizonte  para  Rua Vicente Risola, 1305 | Santa Inês, Belo Horizonte
    Rua João Samaha, 390 | São João Batista (Venda Nova), Belo Horizonte  para  Rua João Samaha, 390 | São João Batista, Belo Horizonte
    Rua Almandina, 56 | Santa Teresa, Belo Horizonte  para  Rua Almandina, 56 | Santa Tereza, Belo Horizonte
    Rua Carlos Sá, 180 | Jardim Atlântico, Belo Horizonte  para  Rua Carlos Sá, 180 | Santa Amelia, Belo Horizonte
    Av. General Carlos Guedes, 165 | Planalto, Belo Horizonte  para  Avenida General Carlos Guedes, 165 | Planalto, Belo Horizonte
    Rua Jefferson de Oliveira, 56 | Santa Amélia, Belo Horizonte  para  Rua Doutor Jefferson de Oliveira, 56 | Santa Amélia, Belo Horizonte
    Rua Pium-I, 686 | Cruzeiro, Belo Horizonte  para  Rua Pium I, 686 | Carmo, Belo Horizonte
    Avenida Padre Vieira, 150 | Minas Brasil, Belo Horizonte  para  Avenida Padre Vieira, 150 | Padre Eustaquio, Belo Horizonte


    Avenida Saramenha, 1599 | Guarani, Belo Horizonte  para  Avenida Saramenha, 1605 | Tupi B, Belo Horizonte
    Rua Ernesto Braga, 2 | Jardim Atlântico, Belo Horizonte  para  Avenida Portugal, 1611 | Santa Amelia, Belo Horizonte 
    Avenida Joaquim Clemente, 682 | Floramar, Belo Horizonte  para  Avenida Joaquim Clemente, 691 | Floramar, Belo Horizonte
    Avenida Francisco Sá, 280 | Prado, Belo Horizonte  para  Avenida Francisco Sá, 272 | Prado, Belo Horizonte
    Rua Álvaro Mata, 466 | Nova Cachoeirinha, Belo Horizonte  para  Rua Conde de Sarzedas, 125 | Nova Cachoeirinha, Belo Horizonte
    Avenida Ressaca, 353 | Coração Eucarístico, Belo Horizonte  para  Rua Padre Nobrega, 20 | Minas Brasil, Belo Horizonte                 lembrar mudar o nome
    Avenida Leontino Francisco Alves, 506 | Serra Verde (Venda Nova), Belo Horizonte  para  Avenida Leontino Francisco Alves, 810 | Serra Verde, Belo Horizonte
    Avenida Itaú, 1195 – Loja A | João Pinheiro, Belo Horizonte  para  Rodovia Anel Rodoviario Celso Mello Azevedo, 1195 | João Pinheiro, Belo Horizonte

'''


CSV_INPUT = "./dados/bares_restaurantes.csv"
CSV_OUTPUT = "./dados/butecos_matched.csv"
JSON_INPUT = "./dados/butecos_data.json"

with open(JSON_INPUT, "r", encoding="utf-8") as f:
    scraped_data = json.load(f)

def parse_text(text_block):
    lines = text_block.split("\n")
    lines = [line.strip() for line in lines if line.strip()]
    nome_fantasia = lines[0] if len(lines) >= 1 else ""
    prato = lines[1] if len(lines) >= 2 else ""
    descricao = lines[2] if len(lines) >= 3 else ""
    endereco_line = ""
    for i, line in enumerate(lines):
        if line.startswith("Endereço:"):
            endereco_line = lines[i+1] if i+1 < len(lines) else ""
            break
    return nome_fantasia, prato, descricao, endereco_line

#normaliza a string do endereco
def normalize(address):
    nfkd_form = unicodedata.normalize('NFKD', address)
    no_accents = ''.join(c for c in nfkd_form if not unicodedata.combining(c))
    return re.sub(r"[^\w]", "", no_accents).lower()

with open(CSV_INPUT, newline="", encoding="utf-8") as f:
    reader = list(csv.DictReader(f, delimiter=";"))

headers = reader[0].keys()
extended_headers = list(headers) + ["PRATO", "DESCRICAO_PRATO", "IMAGEM"]

#Tenta cruzar os dados
for entry in scraped_data:
    nome, prato, descricao, endereco = parse_text(entry["text"])
    image = entry["image"]
    matched = False

    for row in reader:
        #Casamento por nome fantasia
        if normalize(row["NOME_FANTASIA"]) == normalize(nome):
            row["PRATO"] = prato
            row["DESCRICAO_PRATO"] = descricao
            row["IMAGEM"] = image
            matched = True
            break

    #Casamento por endereco
    if not matched and endereco:
        normalized_endereco = normalize(endereco)
        for row in reader:
            tipo_logra = row["DESC_LOGRADOURO"]
            if tipo_logra == "AVE":
                tipo_logra = "AVENIDA"
            elif tipo_logra == "PCA":
                tipo_logra = "PRACA"
            elif tipo_logra == "ROD":
                tipo_logra = "RODOVIA"
            rua = row["NOME_LOGRADOURO"]
            num = row["NUMERO_IMOVEL"]
            bairro = row["NOME_BAIRRO"]
            composed_address = f"{tipo_logra} {rua}, {num} | {bairro}, Belo Horizonte - MG"
            if normalize(composed_address) in normalized_endereco:
                row["PRATO"] = prato
                row["DESCRICAO_PRATO"] = descricao
                row["IMAGEM"] = image
                matched = True
                break
    
    #Nao foi possivel casar os dados, tratar manualmente            
    if not matched:
        print(f"Nao foi possivel casar os dados: {nome} | {endereco}")
        '''
        print(f"{prato}")
        print(f"{descricao}")
        print(f"{image}\n")
        '''


with open(CSV_OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=extended_headers, delimiter=";")
    writer.writeheader()
    for row in reader:
        row.setdefault("PRATO", "")
        row.setdefault("DESCRICAO_PRATO", "")
        row.setdefault("IMAGEM", "")
        writer.writerow(row)
