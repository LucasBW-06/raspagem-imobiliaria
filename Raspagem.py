import requests
from bs4 import BeautifulSoup
from time import sleep
import re
from datetime import datetime

from sqlalchemy import create_engine, select, MetaData, insert, update

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
modalidades = metadata.tables["modalidades"]
tipos = metadata.tables["tipos"]
finalidades = metadata.tables["finalidades"]
utilizacao = metadata.tables["utilizacao"]

lista_links = []
percorrendo = True
pag = 1
while percorrendo:
    print(f"Percorrendo página {pag}...")
    url = f"https://imobiliariafleck.com.br/imoveis/?q=sinop&pagina={pag}&ordem=data"
    response = requests.get(url, timeout=20)
    soup = BeautifulSoup(response.text, 'html.parser')
    if soup.find('div', class_='col-xs-12 alert alert-danger') == None:
        for div in soup.find_all('div', class_='property-item'):
            lista_links.append(div.find('a').get('href'))
        pag += 1
    else:
        percorrendo = False
    sleep(2)

def get_or_create(valor, tabela, coluna):
    if valor is None:
        return None

    with engine.begin() as conexao:
        
        result = conexao.execute(
            select(tabela.c.id).where(getattr(tabela.c, coluna) == valor)
        ).first()

        if result:
            return result[0]

        result = conexao.execute(
            insert(tabela).values({coluna: valor})
        )

        return result.inserted_primary_key[0]

with engine.begin() as conexao:

    imoveis = conexao.execute(
        select(imovel.c.id, imovel.c.link).where(imovel.c.data_removido == None)
    )
    imoveis = imoveis.mappings().all()

    for i in imoveis:
        if i["link"] not in lista_links:
            conexao.execute(
                update(imovel)
                .where(imovel.c.id == ["id"])
                .values(data_removido = datetime.now)
            )


    for link in lista_links:
        print("Visitando link: " + link)
        resultado = conexao.execute(
            select(imovel.c.id).where(imovel.c.link == link)
        )
        if resultado.fetchone():
            continue
        else:
            response = requests.get(link, timeout=20)
            soup = BeautifulSoup(response.text, 'html.parser')

            dados = {}
                
            dados["link"] = link
            dados["localizacao"] = None
            if soup.find('span', class_='location'):
                dados["localizacao"] = soup.find('span', class_='location').text

            mod, val = None, None

            for div in soup.find_all("div", class_="col-sm-6"):
                if div.find('span') and div.find('h2'):
                    mod = div.find('span').text
                    val = div.find('h2').text
                
            dados["modalidade_id"] = get_or_create(mod, modalidades, 'modalidade')

            valor = None
            if val and val != 'CONSULTE AQUI':
                numero = re.search(r'\d[\d.,]*', val).group()
                numero = numero.replace('.', '').replace(',', '.')

                valor = int(float(numero))
                
            dados["valor"] = valor
            dados["tipo_id"] = None
            dados["utilizacao_id"] = None
            dados["finalidade_id"] = None
            dados["area_total"] = None
            dados["area_construida"] = None
            dados["data_inserido"] = datetime.now()

            tabelas = {
                "tipo": tipos,
                "finalidade": finalidades,
                "utilizacao": utilizacao
            }

            for div in soup.find_all('div', class_='col-xs-6 col-sm-4'):
                elemento = div.find('li').text.strip()

                if ":" not in elemento:
                    continue

                key, value = elemento.split(':', 1)
                key = key.strip()
                value = value.strip()

                if key == "TIPO":
                    key = "tipo"
                    dados[key+"_id"] = get_or_create(value, tabelas[key], key)
                    continue
                elif key == "UTILIZAÇÃO":
                    key = "utilizacao"
                    dados[key+"_id"] = get_or_create(value, tabelas[key], key)
                    continue
                elif key == "PERFIL":
                    key = "finalidade"
                    dados[key+"_id"] = get_or_create(value, tabelas[key], key)
                    continue
                elif key == "ÁREA TOTAL":
                    key = "area_total"
                elif key == "CONSTRUÇÃO":
                    key = "area_construida"
                else:
                    continue

                numero = re.search(r"\d+[\.,]?\d*", value)

                if numero:
                    num_str = numero.group().replace(",", "")
                    value = int(float(num_str))
                    
                dados[key] = value

            dados["quantidade_suites"] = None
            dados["quantidade_quartos"] = None
            dados["quantidade_banheiros"] = None
            dados["quantidade_vagas"] = None
            dados["quantidade_cozinhas"] = None
            dados["quantidade_churrasqueira"] = None
            dados["quantidade_escritorio"] = None

            for div in soup.find_all('div', class_='col-xs-6 col-sm-4'):
                if not div.find('i').get('aria-hidden'):
                    key = "".join(re.sub(r'[^a-zA-Zá-úÁ-Ú]', '', div.text))
                    value = int("".join(re.findall(r'\d+', div.text)))
                    if key == "Suítes":
                        dados["quantidade_suites"] = value
                    elif key == "Quartos":
                        dados["quantidade_quartos"] = value
                    elif key == "Banheiros":
                        dados["quantidade_banheiros"] = value
                    elif key == "Vagas":
                        dados["quantidade_vagas"] = value
                    elif key == "Cozinhas":
                        dados["quantidade_cozinhas"] = value
                    elif key == "Churrasqueiras":
                        dados["quantidade_churrasqueira"] = value
                    elif key == "Escritórios":
                        dados["quantidade_escritorio"] = value

            conexao.execute(
                insert(imovel),
                dados
            )
            sleep(2)
    
    conexao.commit()
