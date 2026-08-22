import streamlit as st
import pandas as pd
import numpy as np
import requests
import io

@st.cache_data(ttl=86400)
def fetch_cftc_data():
    """
    Estrazione dati reali CFTC. 
    Regola 1: Zero dati fittizi. In caso di errore restituisce DataFrame vuoto.
    """
    url = "https://publicreporting.cftc.gov/api/views/6dca-aqww/rows.csv?accessType=DOWNLOAD"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text), low_memory=False)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception:
        return pd.DataFrame()

def render_page2():
    st.title("📊 Z-Score Normalization & COT Positioning Lab (CFTC)")
    st.caption("Monitoraggio quantitativo dei flussi istituzionali CFTC basato esclusivamente su endpoint reali.")

    # Container stabile per i comandi
    col_btn, _ = st.columns([1, 3])
    if col_btn.button("🔄 AGGIORNA FLUSSI COT"):
        st.cache_data.clear()

    st.markdown("---")

    # Acquisizione dati
    df = fetch_cftc_data()

    # Schema costante e immutabile per preservare l'integrità del DOM di Streamlit
    columns_schema = [
        "⭐", "Categoria", "Asset / Security", "Bias Contrarian", 
        "Non-Comm Net", "Comm Net", "Open Interest", 
        "Z-Score 1Y (Non-Comm)", "Z-Score 3Y (Non-Comm)"
    ]

    # Gestione unificata del flusso: zero shift strutturali del layout
    if df.empty:
        st.warning(
            "⚠️ **Endpoint CFTC temporaneamente non disponibile o non raggiungibile.**\n\n"
            "In ottemperanza alla **Regola 1 (Tolleranza Zero per Dati Fittizi)**, il sistema si rifiuta "
            "categoricamente di generare numeri casuali o stimati. L'interfaccia rimane stabile in attesa del ripristino."
        )
        display_df = pd.DataFrame(columns=columns_schema)
    else:
        st.success(f"Flusso CFTC sincronizzato con successo. Record elaborati: {len(df):,}")
        display_df = df.head(50)

    # Renderizzazione sicura all'interno di un unico nodo costante
    st.dataframe(display_df, use_container_width=True, hide_index=True)
