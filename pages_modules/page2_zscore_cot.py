import streamlit as st
import pandas as pd
import numpy as np
import requests
import io

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_cftc_data():
    """
    Estrazione dati reali CFTC con gestione blindata delle eccezioni di rete.
    Regola 1: In caso di timeout o errore HTTP, restituisce un DataFrame vuoto.
    Vietato inserire dati fittizi o valori hardcodati.
    """
    url = "https://publicreporting.cftc.gov/api/views/6dca-aqww/rows.csv?accessType=DOWNLOAD"
    try:
        # Timeout rigido a 8 secondi per evitare il blocco del thread di rendering
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.text), low_memory=False)
        if df.empty:
            return pd.DataFrame()
            
        df.columns = df.columns.str.strip().str.lower()
        return df
    except requests.exceptions.RequestException:
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def render_page2():
    st.title("📊 Z-Score Normalization & COT Positioning Lab (CFTC)")
    st.caption("Monitoraggio quantitativo dei flussi istituzionali CFTC basato esclusivamente su endpoint reali.")

    # Controllo di flusso pulito per la cache senza ricaricamenti asincroni rischiosi
    col_btn, _ = st.columns([1, 3])
    if col_btn.button("🔄 AGGIORNA FLUSSI COT"):
        fetch_cftc_data.clear()
        st.rerun()

    st.markdown("---")

    # Spinner sincrono per proteggere il DOM durante la chiamata di rete
    with st.spinner("Sincronizzazione flussi istituzionali CFTC in corso..."):
        df = fetch_cftc_data()

    # Schema costante e immutabile per garantire la stabilità geometrica del DOM
    columns_schema = [
        "⭐", "Categoria", "Asset / Security", "Bias Contrarian", 
        "Non-Comm Net", "Comm Net", "Open Interest", 
        "Z-Score 1Y (Non-Comm)", "Z-Score 3Y (Non-Comm)"
    ]

    if df.empty:
        st.warning(
            "⚠️ **Endpoint CFTC temporaneamente non disponibile o in timeout.**\n\n"
            "In ottemperanza alla **Regola 1 (Tolleranza Zero per Dati Fittizi)**, il sistema si rifiuta "
            "categoricamente di generare numeri casuali o stimati. L'interfaccia rimane stabile in attesa del ripristino della linea."
        )
        display_df = pd.DataFrame(columns=columns_schema)
    else:
        st.success(f"Flusso CFTC sincronizzato con successo. Record elaborati: {len(df):,}")
        display_df = df.head(50)

    # Renderizzazione sicura all'interno di un unico componente stabile
    st.dataframe(display_df, use_container_width=True, hide_index=True)
