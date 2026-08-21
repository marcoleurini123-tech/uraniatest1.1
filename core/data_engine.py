import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data(ttl=3600)
def fetch_eod_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Scarica i dati EOD con caching di 1 ora per evitare chiamate ridondanti."""
    try:
        df = yf.download(ticker, period=period, interval="1d", progress=False)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return pd.DataFrame()

def calculate_eod_poc(df: pd.DataFrame, bins_count: int = 50) -> float:
    """Calcola il Point of Control volumetrico sui dati EOD."""
    if df.empty or 'Close' not in df or 'Volume' not in df:
        return 0.0
    price_bins = np.linspace(df['Low'].min(), df['High'].max(), bins_count)
    bin_idx = np.digitize(df['Close'].values, price_bins)
    vol_hist = np.zeros(len(price_bins))
    for idx, v in zip(bin_idx, df['Volume'].values):
        if idx < len(vol_hist):
            vol_hist[idx] += v
    return float(price_bins[np.argmax(vol_hist)])
