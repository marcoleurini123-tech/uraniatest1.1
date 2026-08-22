import os
import io
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import streamlit as st

DB_FILE = "macro_data.csv"

def fetch_bridge_data():
    """Recupera i flussi di liquidità da Google Sheets tramite URL sicuro in st.secrets."""
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
    except Exception as e:
        st.error(f"Errore critico Data Fetching (Bridge): {e}")
        return pd.DataFrame(columns=["Data", "Net_Liquidity", "M2", "RRP", "TGA", "WALCL"])

def fetch_yahoo_macro(days=252):
    """Estrazione serie storiche EOD da Yahoo Finance. Nessun hardcoding."""
    tickers = {
        "VIX1D": "^VIX1D", "VIX": "^VIX", "VVIX": "^VVIX", "SKEW": "^SKEW", "MOVE": "^MOVE", 
        "DXY": "DX-Y.NYB", "SPY": "SPY", "RSP": "RSP", "XLY": "XLY", "XLP": "XLP", 
        "HYG": "HYG", "TLT": "TLT", "LQD": "LQD", "P_C": "^PCCR", "GLD": "GLD", 
        "USO": "USO", "CPER": "CPER", "US2Y": "^IRX", "US10Y": "^TNX", 
        "BDRY": "BDRY", "SOXX": "SOXX", "BTC": "BTC-USD"
    }
    try:
        data = yf.download(list(tickers.values()), period=f"{days}d", interval="1d", progress=False)['Close']
        if isinstance(data, pd.Series):
            data = data.to_frame()
        data = data.rename(columns={v: k for k, v in tickers.items()})
        data.index = pd.to_datetime(data.index).tz_localize(None).normalize()
        return data.reset_index().rename(columns={'Date': 'Data', 'index': 'Data'})
    except Exception as e:
        st.error(f"Errore critico Data Fetching (Yahoo): {e}")
        return pd.DataFrame(columns=["Data"])

def fetch_squeezemetrics():
    """Estrazione Dark Pool (DIX) e Gamma (GEX)."""
    try:
        d_d = pd.read_csv("https://squeezemetrics.com/monitor/static/DIX.csv").tail(252)
        d_d = d_d.rename(columns={'date':'Data','dix':'DIX','gex':'GEX'})
        d_d['Data'] = pd.to_datetime(d_d['Data']).dt.normalize()
        d_d['DIX'] = d_d['DIX'] * 100
        return d_d
    except Exception as e:
        st.error(f"Errore critico Data Fetching (SqueezeMetrics): {e}")
        return pd.DataFrame(columns=["Data", "DIX", "GEX"])

def sync_macro_database():
    """Allineamento e salvataggio del database EOD."""
    d_y = fetch_yahoo_macro()
    d_b = fetch_bridge_data()
    d_d = fetch_squeezemetrics()
    
    new_df = pd.merge(d_y, d_d, on='Data', how='outer')
    new_df = pd.merge(new_df, d_b, on='Data', how='outer')
    new_df = new_df.sort_values("Data").ffill(limit=3)
    new_df.to_csv(DB_FILE, index=False)
    return new_df
