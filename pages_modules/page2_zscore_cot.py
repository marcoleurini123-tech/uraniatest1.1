import streamlit as st
import pandas as pd
import numpy as np

# =============================================================================
# CATALOGO ASSET CFTC UFFICIALI
# =============================================================================
CFTC_UNIVERSE = {
    "🇺🇸 Indici Azionari": [
        "NASDAQ-100", "S&P 500", "DOW JONES INDUSTRIAL AVERAGE", "RUSSELL 2000"
    ],
    "🏛️ Obbligazionario & Tassi USA": [
        "US TREASURY BONDS", "US TREASURY 10Y NOTES", "US TREASURY 5Y NOTES"
    ],
    "🥇 Metalli Preziosi": [
        "GOLD", "SILVER", "COPPER"
    ],
    "🛢️ Energetici": [
        "CRUDE OIL, LIGHT SWEET", "NATURAL GAS"
    ],
    "💱 Valute (FX Futures)": [
        "USD INDEX", "EURO FX", "BRITISH POUND", "JAPANESE YEN"
    ]
}

def fetch_cftc_data():
    """
    Funzione di Data Fetching isolata. 
    Rispetta la Regola 1: In caso di assenza o errore, restituisce un DataFrame vuoto,
    senza inserire dati fittizi o casuali.
    """
    try:
        # Placeholder per chiamata API reale o caricamento file istituzionale
        # Se l'endpoint non è raggiungibile, solleva eccezione gestita
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

# =============================================================================
# INTERFACCIA UI STREAMLIT (Pagina 2)
# =============================================================================
def render_page2():
    st.title("📊 Z-Score Normalization & COT Positioning Lab (CFTC)")
    st.caption("Monitoraggio quantitativo dei flussi istituzionali CFTC basato su dati reali.")

    st.markdown("---")

    raw_df = fetch_cftc_data()

    if raw_df.empty:
        st.warning(
            "⚠️ **Sorgente Dati CFTC non attiva o in fase di sincronizzazione.** "
            "In ottemperanza alla tolleranza zero per i dati fittizi (Regola 1), "
            "il terminale non genera valori casuali o stimati."
        )
        
        # Tabella di fallback strutturata per mantenere l'integrità del DOM di Streamlit
        df_empty = pd.DataFrame(columns=[
            "⭐", "Categoria", "Asset / Security", "Bias Contrarian", 
            "Non-Comm Net", "Comm Net", "Open Interest", 
            "Z-Score 1Y (Non-Comm)", "Z-Score 3Y (Non-Comm)"
        ])
        st.dataframe(df_empty, use_container_width=True, hide_index=True)
        return

    st.subheader("Tabella Analitica Posizionamento")
    st.dataframe(raw_df, use_container_width=True, hide_index=True)

