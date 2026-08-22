import os
import io
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import streamlit as st

DB_FILE = "macro_data.csv"

def fetch_bridge_data():
    """Recupera i dati macroeconomici dal Google Sheets tramite st.secrets."""
    try:
        url = st.secrets["GOOGLE_BRIDGE_URL"]
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        df_b = pd.read_csv(io.StringIO(response.text))
        df_b.columns = df_b.columns.str.strip()
        df_b = df_b.rename(columns={'Date': 'Data', 'data': 'Data'})
        
        if pd.api.types.is_numeric_dtype(df_b['Data']):
            df_b['Data'] = pd.to_datetime(df_b['Data'], unit='D', origin='1899-12-30')
        else:
            df_b['Data'] = pd.to_datetime(df_b['Data'], errors='coerce')
            
        df_b['Data'] = df_b['Data'].dt.normalize()
        
        for col in ['Net_Liquidity', 'M2', 'RRP', 'TGA', 'WALCL']:
            if col in df_b.columns:
                df_b[col] = pd.to_numeric(df_b[col], errors='coerce')
                
        return df_b.dropna(subset=['Data', 'Net_Liquidity'])
    except Exception:
        return pd.DataFrame(columns=["Data", "Net_Liquidity", "M2", "RRP", "TGA", "WALCL"])

def fetch_yahoo_macro(days=252):
    """Estrazione serie storiche EOD da Yahoo Finance con gestione delle eccezioni per singolo ticker."""
    tickers = {
        "VIX": "^VIX", "VVIX": "^VVIX", "SKEW": "^SKEW", "MOVE": "^MOVE", 
        "DXY": "DX-Y.NYB", "SPY": "SPY", "RSP": "RSP", "XLY": "XLY", "XLP": "XLP", 
        "HYG": "HYG", "TLT": "TLT", "LQD": "LQD", "GLD": "GLD", 
        "USO": "USO", "CPER": "CPER", "US2Y": "^IRX", "US10Y": "^TNX", 
        "BDRY": "BDRY", "SOXX": "SOXX", "BTC": "BTC-USD"
    }
    
    data_frames = {}
    for key, ticker in tickers.items():
        try:
            df_t = yf.download(ticker, period=f"{days}d", interval="1d", progress=False)
            if not df_t.empty and 'Close' in df_t.columns:
                s = df_t['Close']
                if isinstance(s, pd.DataFrame):
                    s = s.iloc[:, 0]
                data_frames[key] = s
        except Exception:
            continue

    if not data_frames:
        return pd.DataFrame(columns=["Data"])

    data = pd.DataFrame(data_frames)
    data.index = pd.to_datetime(data.index).tz_localize(None).normalize()
    return data.reset_index().rename(columns={'index': 'Data', 'Date': 'Data'})

def calculate_zscore(series, window=52):
    """Calcolo matematico rigoroso dello Z-Score su finestra mobile."""
    mean = series.rolling(window=window, min_periods=10).mean()
    std = series.rolling(window=window, min_periods=10).std()
    return (series - mean) / (std + 1e-9)

def render_page1():
    st.title("Macro Intelligence & Liquidità Fed")
    st.caption("Terminal EOD • Monitoraggio flussi istituzionali e regimi macroeconomici.")

    if st.button("🔄 SINCRONIZZA FLUSSI EOD AUTOMATICI"):
        st.cache_data.clear()
        with st.spinner("Estrazione dati da API reali in corso..."):
            df_y = fetch_yahoo_macro()
            df_b = fetch_bridge_data()
            if not df_y.empty:
                df_merged = df_y.copy()
                if not df_b.empty:
                    df_merged = pd.merge(df_merged, df_b, on='Data', how='outer')
                df_merged = df_merged.sort_values("Data").ffill(limit=3)
                df_merged.to_csv(DB_FILE, index=False)
        st.rerun()

    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Data'] = pd.to_datetime(df['Data'])
        
        st.subheader("Monitor Tensioni (Z-Score Storico)")
        
        # Esempio di metrica calcolata con Z-Score rigoroso
        if 'VIX' in df.columns:
            df['VIX_Z'] = calculate_zscore(df['VIX'], window=52)
            last_vix = df['VIX'].iloc[-1]
            last_z = df['VIX_Z'].iloc[-1]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("VIX Spot", f"{last_vix:.2f}", f"Z-Score: {last_z:+.2f}")
    else:
        st.warning("Database macro assente. Eseguire la sincronizzazione manuale.")
