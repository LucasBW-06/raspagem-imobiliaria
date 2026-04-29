import requests
from bs4 import BeautifulSoup
from time import sleep

lista = []
percorrendo = True
pag = 1

while percorrendo:
    url = f"https://www.ruacep.com.br/mt/sinop/bairros/{pag}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }
    response = requests.get(url, timeout=20, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    for div in soup.find_all('div', class_='card-header'):
        lista.insert(0, div.find('strong').text)

    if soup.find('a', class_='page-link hide-on-mobile').text in 'Última':
        pag += 1
    else:
        percorrendo = False

print(lista)
    