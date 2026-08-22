import pandas as pd
import numpy as np
import requests
import io
import yfinance as yf

def fetch_cftc_real_data():
    """
    Estrae i dati reali CFTC Legacy dai report pubblici ufficiali.
    Conforme alla Regola 1: in caso di timeout o errore di rete, restituisce 
    un DataFrame vuoto. Vietato categoricamente l'uso di numeri casuali o hardcodati.
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

def calculate_z_score(series: pd.Series, window: int = 52) -> pd.Series:
    """
    Conforme alla Regola 2: Rigore Matematico e Z-Score.
    Calcola la deviazione standard normalizzata (Z-Score) su finestre temporali 
    rolling (es. 52 settimane per 1Y o 156 settimane per 3Y), senza soglie percentuali fisse.
    """
    mean = series.rolling(window=window, min_periods=10).mean()
    std = series.rolling(window=window, min_periods=10).std()
    return (series - mean) / (std + 1e-9)

def fetch_eod_macro_series(ticker: str, period: str = "2y") -> pd.Series:
    """
    Estrae serie storiche EOD reali tramite yfinance.
    Conforme alla Regola 1: se il ticker fallisce o viene delistato, 
    restituisce una serie vuota senza bloccare l'esecuzione globale.
    """
    try:
        df = yf.download(ticker, period=period, interval="1d", progress=False)
        if df.empty or 'Close' not in df.columns:
            return pd.Series(dtype=float)
        series = df['Close']
        if isinstance(series, pd.DataFrame):
            series = series.iloc[:, 0]
        return series
    except Exception:
        return pd.Series(dtype=float)
