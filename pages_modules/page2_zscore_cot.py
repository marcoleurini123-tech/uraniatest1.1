import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import requests

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

@st.cache_data(ttl=86400)
def fetch_cftc_data():
    """
    Estrazione dati reali CFTC. 
    REGOLA 1: Se l'endpoint istituzionale non risponde o fallisce, 
    restituisce un DataFrame vuoto. Vietato inserire dati fittizi o casuali.
    """
    try:
        url = "https://publicreporting.cftc.gov/api/views/6dca-aqww/rows.csv?accessType=DOWNLOAD"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text), low_memory=False)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception:
        return pd.DataFrame()

# =============================================================================
# INTERFACCIA UI STREAMLIT (Pagina 2)
# =============================================================================
def render_page2():
    st.title("📊 Z-Score Normalization & COT Positioning Lab (CFTC)")
    st.caption("Monitoraggio quantitativo dei flussi istituzionali CFTC basato esclusivamente su dati reali.")

    col_sync, _ = st.columns([1, 3])
    if col_sync.button("🔄 AGGIORNA FLUSSI COT"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    raw_df = fetch_cftc_data()

    # Controllo difensivo anti-crash: nessun dato inventato, gestione pulita dello stato vuoto
    if raw_df.empty:
        st.warning(
            "⚠️ **Endpoint CFTC temporaneamente non disponibile o in fase di sincronizzazione.** "
            "In ottemperanza alla Regola 1 (Anti-Allucinazione), il sistema rifiuta categoricamente "
            "di generare dati fittizi o stimati. L'operatività riprenderà automaticamente al ripristino del flusso."
        )
        
        # Tabella di fallback strutturata per proteggere il DOM di Streamlit da eccezioni di rendering
        df_empty = pd.DataFrame(columns=[
            "⭐", "Categoria", "Asset / Security", "Bias Contrarian", 
            "Non-Comm Net", "Comm Net", "Open Interest", 
            "Z-Score 1Y (Non-Comm)", "Z-Score 3Y (Non-Comm)"
        ])
        st.dataframe(df_empty, use_container_width=True, hide_index=True)
        return

    st.subheader("Tabella Analitica Posizionamento Istituzionale")
    st.dataframe(raw_df.head(50), use_container_width=True, hide_index=True)
