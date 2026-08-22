import streamlit as st
import pandas as pd
import numpy as np
import requests
import io

def fetch_cftc_data():
    """
    Modulo di Data Fetching (Regola 1 & Regola 4).
    Esegue la chiamata all'endpoint ufficiale CFTC.
    In caso di fallimento o assenza di connessione, restituisce un DataFrame vuoto 
    senza ricorrere a simulazioni o dati fittizi.
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
    """
    Modulo UI per il Lab COT e Z-Score.
    Progettato con programmazione difensiva per impedire qualsiasi crash del DOM.
    """
    st.title("📊 Z-Score Normalization & COT Positioning Lab (CFTC)")
    st.caption("Monitoraggio quantitativo dei flussi istituzionali CFTC basato esclusivamente su endpoint reali.")

    col_btn, _ = st.columns([1, 3])
    if col_btn.button("🔄 AGGIORNA FLUSSI COT"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    # Estrazione dati tramite la funzione isolata
    df = fetch_cftc_data()

    # Controllo difensivo dello stato del dataset
    if df.empty:
        st.warning(
            "⚠️ **Endpoint CFTC temporaneamente non disponibile o non raggiungibile.**\n\n"
            "In ottemperanza alla **Regola 1 (Tolleranza Zero per Dati Fittizi)**, il sistema si rifiuta "
            "categoricamente di generare numeri casuali o stimati. L'operatività riprenderà automaticamente "
            "non appena il flusso istituzionale sarà ripristinato."
        )
        return

    # Renderizzazione sicura dei dati reali se disponibili
    st.success(f"Flusso CFTC sincronizzato con successo. Record elaborati: {len(df):,}")
    st.dataframe(df.head(50), use_container_width=True, hide_index=True)
