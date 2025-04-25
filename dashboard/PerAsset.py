import streamlit as st
import pandas as pd
import plotly.express as px

# Chargement des données
histo = pd.read_csv(r'files\History.csv')
histo["Date"] = pd.to_datetime(histo['Date'])

basicInfo = pd.read_csv(r'files\informations.csv')
basicInfo['compte'] = 1
basicInfo.loc[basicInfo['market'].str.contains('us_', na=False), 'Marché'] = "United States"
basicInfo.loc[basicInfo['market'].str.contains('fr_', na=False), 'Marché'] = "France"

# Configuration de la page
st.set_page_config(page_title="Recap per Asset", page_icon="", layout="wide")
st.title("Par Actif")
ss = st.selectbox('Choose Your Asset',options= basicInfo['shorName'].unique())
infomation = basicInfo[basicInfo['shorName']==ss]
ticker = infomation['ticker'].iloc[0]
historiquePerAsset = histo[histo['ticket']==ticker]
kpi1,kpi2,kpi4,kpi5 = st.columns(4)
latest = histo[(histo['ticket']==ticker) & histo['LatestDate']==True]["price"].sum()
poids =  latest / histo[(histo['ticket']==ticker) & histo['LatestDate']==True]["Close"].sum()
with kpi1 :
     st.metric(label="Sector",value = f"{infomation['sector'].iloc[0]}")
with kpi2 :
     st.metric(label="Price", value = f"$ {round(latest,2)}")
with kpi4 :
     st.metric(label="Poids de l'action", value= f"{round(poids*100,2)}%")

