import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Chargement des données
histo = pd.read_csv('data/raw/History.csv')
histo["Date"] = pd.to_datetime(histo['Date'])

basicInfo = pd.read_csv('data/raw/informations.csv')
basicInfo['compte'] = 1
basicInfo.loc[basicInfo['market'].str.contains('us_', na=False), 'Marché'] = "United States"
basicInfo.loc[basicInfo['market'].str.contains('fr_', na=False), 'Marché'] = "France"

# Configuration de la page
st.set_page_config(page_title="Par Actif", page_icon="📈", layout="wide")
st.sidebar.header("Par Actif 📈")

st.title("Par Actif")
ss = st.selectbox('Choose Your Asset',options= basicInfo['shortName'].unique())
infomation = basicInfo[basicInfo['shortName']==ss]
ticker = infomation['ticker'].iloc[0]
historiquePerAsset = histo[histo['ticket']==ticker]

kpi1,kpi2,kpi4,kpi5,kpi3 = st.columns(5)
latest = histo[(histo['ticket']==ticker) & histo['LatestDate']==True]["price"].sum()
initialPrice = histo[(histo['ticket']==ticker) & histo['EntryDate']==True]["price"].sum()
price = histo[(histo['ticket']==ticker) & histo['EntryDate']==True]["price"].sum() / histo[(histo['ticket']==ticker) & histo['EntryDate']==True]["Close"].sum()
Var = (latest / initialPrice)-1

with kpi1 :
     st.metric(label="Sector",value = f"{infomation['sector'].iloc[0]}")
with kpi2 :
     st.metric(label="Price", value = f"$ {round(latest,2)}")
with kpi4 :
     st.metric(label="Poids de l'action", value= f"{round(price*100,2)}%")
with kpi5 :
     st.metric(label='Performance', value=f"{round(Var *100,2)} %")
with kpi3 :
     st.metric(label="Gain Latent", value=f"$ {round(latest-initialPrice,2)}")

col1,col2 = st.columns([3,1])

with col1 :
     fig_line = px.line(historiquePerAsset,'Date','price',range_y=[historiquePerAsset['price'].min() - 5, historiquePerAsset['price'].max() +5])
     st.plotly_chart(fig_line)

with col2 :
     fig = go.Figure()
     fig.add_trace(go.Bar(name="Investi", x=[ss], y=[initialPrice], marker_color='lightblue'))
     fig.add_trace(go.Bar(name="Valeur actuelle", x=[ss], y=[round(latest,2)], marker_color='green'))
     fig.update_layout(barmode='group', title="Investi vs Valeur actuelle")
     st.plotly_chart(fig)

st.html(f"<h2><b>Objectif</b> : $ {round(histo[(histo['ticket']==ticker) & histo['EntryDate']==True]["price"].sum())*2} </h2>")