import streamlit as st
import pandas as pd
import plotly.express as px

# Chargement des données
histo = pd.read_csv('/home/jathur/Bureau/Projects/TeleFinance/files/History.csv')
histo["Date"] = pd.to_datetime(histo['Date'])

basicInfo = pd.read_csv('/home/jathur/Bureau/Projects/TeleFinance/files/informations.csv')
basicInfo['compte'] = 1
basicInfo.loc[basicInfo['market'].str.contains('us_', na=False), 'Marché'] = "United States"
basicInfo.loc[basicInfo['market'].str.contains('fr_', na=False), 'Marché'] = "France"

# Calcul des KPI
valeur_portefeuille = round(histo[histo['Date'] == histo['Date'].max()]['price'].sum(), 2)
nb_actifs = len(basicInfo)
nb_secteurs = basicInfo['sector'].nunique()
part_us = round(
    basicInfo[basicInfo['Marché'] == "United States"].shape[0] / len(basicInfo) * 100, 1
)
Val = histo[histo['EntryDate']==True]['price'].sum()
ValFini = histo[histo['LatestDate']==True]['price'].sum()
variation = round((ValFini - Val) / Val * 100, 2)
gain_latent = round(ValFini - Val, 2)
rendement_moyen = round((ValFini - Val) / nb_actifs, 2)



# Configuration de la page
st.set_page_config(page_title="Daily Recap", page_icon="📈", layout="wide")
st.title("📊 Daily Recap")

# 🧮 KPIs pleine largeur
kpi1, kpi2, kpi3, kpi4,kpi5 = st.columns(5)
with kpi1:
    st.metric("💰 Valorisation totale", f"$ {valeur_portefeuille:,.2f}", delta=variation)
with kpi2:
    st.metric("📦 Actifs détenus", f"{nb_actifs}")
with kpi3:
    st.metric("🏷️ Secteurs couverts", f"{nb_secteurs}")
with kpi4:
    st.metric("💸 Gain latent", f"$ {gain_latent:,.2f}")
with kpi5:
    st.metric("📉 Rendement/actif", f" $ {rendement_moyen:,.2f}")


# 📈 Graphique d'évolution + pie charts
st.subheader("Évolution journalière du portefeuille")
getHist = histo.groupby('Date', as_index=False).agg({"price": "sum"})
st.line_chart(getHist, x="Date", y="price")


# 🥧 Répartition sectorielle et géographique
col_pie1, col_pie2, col_bar = st.columns(3)

with col_pie1:
    st.subheader("Répartition par secteur")
    sectorCount = basicInfo.groupby('sector', as_index=False).agg({"compte": "sum"})
    fig1 = px.pie(sectorCount, values="compte", names='sector')
    st.plotly_chart(fig1, use_container_width=True)

with col_pie2:
    st.subheader("Répartition par marché")
    PerMarket = basicInfo.groupby('Marché', as_index=False).agg({"compte": "sum"})
    fig2 = px.pie(PerMarket, values='compte', names='Marché')
    st.plotly_chart(fig2, use_container_width=True)

with col_bar:
    st.subheader("Montant investi par secteur")
    invest_sector = histo.merge(basicInfo[['ticker', 'shorName']], left_on="ticket", right_on='ticker', how='left')
    invest_sector = invest_sector[invest_sector['Date'] == invest_sector['Date'].max()]
    agg_sector = invest_sector.groupby('shorName', as_index=False).agg({'price': 'sum'}).sort_values(by='price', ascending=False).head(10)
    fig3 = px.bar(agg_sector, x='shorName', y='price', title="Montant investi par secteur", text_auto='.2s')
    fig3.update_layout(xaxis_title=None, yaxis_title="Montant (€)", title_x=0.2)
    st.plotly_chart(fig3, use_container_width=True)