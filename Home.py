import streamlit as st
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="🏠 TéléFinance - Accueil",
    page_icon="💼",
    layout="centered",
)

# En-tête principal
st.title("💼 TéléFinance - Dashboard Personnel")

st.markdown(
    """
Bienvenue sur ton espace d'analyse financière personnel.  
Suivi en temps réel de ton portefeuille d'actifs.

---

### 🚀 Accès rapide :
- 📊 **[Daily Recap]** : Vue d'ensemble de ta performance globale
- 📈 **[Analyse par Actif]** : Focus détaillé sur chaque investissement
"""
)

# Encadré d'infos utiles
with st.container():
    st.info(
        f"""
        📅 **Date** : {datetime.now().strftime('%d/%m/%Y')}  
        📈 **Dernière mise à jour** : {(datetime.now().strftime('%H:%M'))}
        
        _Utilise le menu latéral (à gauche) pour naviguer entre les sections._
        """
    )

# Optionnel : image ou logo
# st.image("path/to/your/logo.png", width=150)
