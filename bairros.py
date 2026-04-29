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

bairros = metadata.tables["bairros"]

lista = []

with engine.begin() as conn:
    with open("lista_bairros.txt", "r", encoding="utf-8") as f:
        for linha in f:
            dados = {'bairro': linha.replace('\n', '')}
            conn.execute(
                insert(bairros),
                dados
            )
