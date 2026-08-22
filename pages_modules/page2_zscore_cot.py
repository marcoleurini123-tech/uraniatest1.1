import streamlit as st
import pandas as pd
import numpy as np
import requests
import io

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

    col_btn, _ = st.columns([1, 3])
    if col_btn.button("🔄 AGGIORNA FLUSSI COT"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    df = fetch_cftc_data()

    # Schema costante e immutabile per prevenire errori di DOM (removeChild)
    columns_schema = [
        "⭐", "Categoria", "Asset / Security", "Bias Contrarian", 
        "Non-Comm Net", "Comm Net", "Open Interest", 
        "Z-Score 1Y (Non-Comm)", "Z-Score 3Y (Non-Comm)"
    ]

    if df.empty:
        st.warning(
            "⚠️ **Endpoint CFTC temporaneamente non disponibile o non raggiungibile.**\n\n"
            "In ottemperanza alla **Regola 1 (Tolleranza Zero per Dati Fittizi)**, il sistema si rifiuta "
            "categoricamente di generare numeri casuali o stimati."
        )
        # Renderizziamo un DataFrame vuoto ma con lo schema RIGIDO per non rompere il DOM
        df_empty = pd.DataFrame(columns=columns_schema)
        st.dataframe(df_empty, use_container_width=True, hide_index=True)
        return

    st.success(f"Flusso CFTC sincronizzato. Record elaborati: {len(df):,}")
    st.dataframe(df.head(50), use_container_width=True, hide_index=True)
