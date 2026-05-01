import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text, MetaData
import altair as alt
 
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
bairros = metadata.tables["bairros"]

with engine.begin() as conn:
    query = text("""
            SELECT t.tipo AS tipo, COUNT(*) AS quantidade FROM imoveis i
            LEFT JOIN tipos t ON i.tipo_id = t.id
            GROUP BY tipo
            ORDER BY quantidade DESC
        """)

    data_hard = pd.read_sql_query(query, conn)

    label_chart = alt.Chart(data_hard).mark_text(
                align='left',
                baseline='middle',
                dx=3  
            ).encode(
                x=alt.X('quantidade:Q'),
                y=alt.Y('tipo:N', sort='-x'),
                text='quantidade:Q'
            )
            
    chart = alt.Chart(data_hard).mark_bar().encode(
                x=alt.X('quantidade:Q', axis=alt.Axis(title='Quantidade')),
                y=alt.Y('tipo:N', sort='-x', axis=alt.Axis(title='Tipos')),
                color=alt.value('#66a3ff'),
                tooltip=['quantidade:Q', 'tipo:N']  
            ).properties(
                width=500
            )
            
    combined_chart = (chart + label_chart ).properties(title='Tipos')
            
    st.altair_chart(combined_chart, use_container_width=True)

    query = text("""
                SELECT
                SUM(CASE WHEN i.localizacao IS NULL THEN 1 ELSE 0 END) AS sem_endereco,
                SUM(CASE WHEN i.localizacao IS NOT NULL THEN 1 ELSE 0 END) AS com_endereco
                FROM imoveis i;
                       """)
    
    data = pd.read_sql_query(query, conn)

    data= pd.DataFrame({
    'tipo': ['Sem endereço', 'Com endereço'],
    'quantidade': [
        data['sem_endereco'][0],
        data['com_endereco'][0]
    ]})

    data['percentual'] = (
    data['quantidade'] / data['quantidade'].sum())

    chart = alt.Chart(data).mark_arc(innerRadius=50).encode(
    theta=alt.Theta('quantidade:Q'),
    color=alt.Color('tipo:N', title='Situação'),
    tooltip=[
        alt.Tooltip('tipo:N', title='Tipo'),
        alt.Tooltip('quantidade:Q', title='Quantidade'),
        alt.Tooltip('percentual:Q', title='Percentual', format='.1%')
    ])

    label_chart = alt.Chart(data).mark_text(radius=120).encode(
    theta=alt.Theta('quantidade:Q'),
    text=alt.Text('percentual:Q', format='.1%'),
    color=alt.value("black"))

    combined_chart = (chart + label_chart ).properties(title='Comparação de imóveis com e sem endereço')

    st.altair_chart(combined_chart, use_container_width=True)

    query_venda = text("""
                SELECT b.bairro, AVG(i.valor) AS media FROM imoveis i
                LEFT JOIN bairros b ON i.bairro_id = b.id
                LEFT JOIN modalidades m ON i.modalidade_id = m.id
                WHERE m.modalidade = "VENDA" AND i.valor IS NOT NULL AND b.bairro IS NOT NULL
                GROUP BY b.bairro
                       """)
    
    query_locacao = text("""
                SELECT b.bairro, AVG(i.valor) AS media FROM imoveis i
                LEFT JOIN bairros b ON i.bairro_id = b.id
                LEFT JOIN modalidades m ON i.modalidade_id = m.id
                WHERE m.modalidade = "LOCAÇÃO" AND i.valor IS NOT NULL AND b.bairro IS NOT NULL
                GROUP BY b.bairro
                       """)
    
    data_venda = pd.read_sql_query(query_venda, conn)
    data_locacao = pd.read_sql_query(query_locacao, conn)

    chart = alt.Chart(data_venda).mark_bar().encode(
    x=alt.X('bairro:N', title='Bairro', sort='-y'),
    y=alt.Y('media:Q', 
            title='Valor médio'),
    tooltip=[
        alt.Tooltip('bairro:N', title='Bairro'),
        alt.Tooltip('media:Q', title='Valor Médio')
        ]
).properties(
    width=600
)
    
    st.altair_chart(chart.properties(title="Média dos valores de venda por bairro"), use_container_width=True)

    chart = alt.Chart(data_locacao).mark_bar().encode(
    x=alt.X('bairro:N', title='Bairro', sort='-y'),
    y=alt.Y('media:Q', 
            title='Valor médio'),
    tooltip=[
        alt.Tooltip('bairro:N', title='Bairro'),
        alt.Tooltip('media:Q', title='Valor Médio')
        ]
).properties(
    width=600
)

    st.altair_chart(chart.properties(title="Média dos valores de locação por bairro"), use_container_width=True)