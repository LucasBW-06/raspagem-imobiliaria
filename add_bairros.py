import re
import unicodedata
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, select, MetaData, update

username = "root"
password = "admin"
host = "localhost"
port = 3306
database = "imobiliaria"

connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_string)

metadata = MetaData()

metadata.reflect(bind=engine)

imovel = metadata.tables["imoveis"]
bairros = metadata.tables["bairros"]

def normalizar(texto):
    texto = texto.upper()
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return texto

def extrair_bairro(endereco, lista_bairros):
    texto = normalizar(endereco)
    texto_split = texto.split()

    melhor_bairro = None
    maior_score = 0
    repeticoes = 0

    for item in lista_bairros:
        bairro_norm = normalizar(item['bairro'])

        # quebra em palavras relevantes
        palavras = re.sub(r'\b(SINOP|DE|DAS|DOS|DA|DO)\b', '', bairro_norm).strip().split()

        # conta quantas palavras do bairro aparecem no endereço
        score = 0
        for p in palavras:
            if p in texto_split:
                score += 1

        # bônus se o nome completo aparecer
        if bairro_norm in texto:
            score += 100

        if score == maior_score and maior_score > 0:
            repeticoes += 1

        if score > maior_score:
            maior_score = score
            melhor_bairro = item['id']
            repeticoes = 0
    
    if maior_score < 100 and 'CENTRO' in texto_split:
        melhor_bairro = 129
        maior_score = 100

    if maior_score > 0 and repeticoes == 0:
        return melhor_bairro
    else:
        return None

def buscar_titulo(url):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                  }
    response = requests.get(url, timeout=20, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    return soup.find('h4', class_='detail-title').text

with engine.begin() as conn:

    imoveis = conn.execute(
        select(imovel.c.id, imovel.c.localizacao, imovel.c.link).where(imovel.c.bairro_id == None)
    )
    imoveis = imoveis.mappings().all()

    lista = conn.execute(
            select(bairros.c.id, bairros.c.bairro))
    lista = lista.mappings().all()

    for i in imoveis:
        bairro = ''
        if i["localizacao"] == None:
            titulo = buscar_titulo(i["link"])
            bairro = extrair_bairro(titulo, lista)
        else:
            bairro = extrair_bairro(i["localizacao"], lista)
        
        if bairro != None:
                conn.execute(
                        update(imovel)
                        .where(imovel.c.id == i["id"])
                        .values(bairro_id = bairro)
                    )
    conn.commit()
    conn.close()

print("Concluido")