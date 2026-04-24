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



with engine.begin() as conn:
    query = text("""
            SELECT t.tipo AS tipo, COUNT(*) AS quantidade FROM imoveis i
            LEFT JOIN tipos t ON i.tipo_id = t.id
            GROUP BY tipo
            ORDER BY quantidade DESC
        """)

    data_hard = pd.read_sql_query(query, conn)

    max_desc_length = data_hard['tipo'].apply(len).max()

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