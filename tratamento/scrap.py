import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time

BASE_URL = "https://comidadibuteco.com.br/butecos/belo-horizonte"
NUM_PAGES = 11
headers = {'User-Agent': 'Mozilla/5.0'}

all_data = []

for i in range(1, NUM_PAGES + 1):
    if i == 1:
        url = BASE_URL + "/"
    else:
        url = f"{BASE_URL}/page/{i}/"

    #pagina atual principal
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    items = soup.find_all("div", class_="item")

    for item in items:
        a_tag = item.find("a", string="Detalhes")
        img_tag = item.find("img")

        if a_tag:
            detail_url = urljoin(url, a_tag["href"])
            image_url = urljoin(url, img_tag["src"]) if img_tag else None

            try:
                #pagina do hiperlink detalhes
                res = requests.get(detail_url, headers=headers)
                page_soup = BeautifulSoup(res.content, "html.parser")
                main = page_soup.find("main", class_="content")

                if main:
                    bar_info = {
                        "url": detail_url,
                        "image": image_url,
                        "text": main.get_text(separator="\n", strip=True)
                    }
                    all_data.append(bar_info)

                time.sleep(1)

            except Exception as e:
                print(f"Erro scraping {detail_url}: {e}")

with open("butecos_data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print(f"\n{len(all_data)} itens salvos em 'butecos_data.json'")
