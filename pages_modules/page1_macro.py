import os
import io
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

DB_FILE = "macro_data.csv"

# ==========================================
# FASE 1: DATA FETCHING (ESTRAZIONE REALE)
# ==========================================
def fetch_bridge_data():
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
    d_y = fetch_yahoo_macro()
    d_b = fetch_bridge_data()
    d_d = fetch_squeezemetrics()
    
    new_df = pd.merge(d_y, d_d, on='Data', how='outer')
    new_df = pd.merge(new_df, d_b, on='Data', how='outer')
    new_df = new_df.sort_values("Data").ffill(limit=3)
    new_df.to_csv(DB_FILE, index=False)
    return new_df


# ==========================================
# FASE 2: MOTORE MATEMATICO (Z-SCORE)
# ==========================================
def calculate_rolling_zscore(series, window=156):
    rolling_mean = series.rolling(window=window, min_periods=20).mean()
    rolling_std = series.rolling(window=window, min_periods=20).std()
    return (series - rolling_mean) / rolling_std

def apply_math_engine(df):
    df['Data'] = pd.to_datetime(df['Data'])
    df = df.sort_values("Data")
    
    if 'Net_Liquidity' in df.columns:
        df['Liq_Delta_5D'] = df['Net_Liquidity'].pct_change(periods=5) * 100.0
        df['Liq_Delta_30D'] = df['Net_Liquidity'].pct_change(periods=20) * 100.0
    else:
        df['Liq_Delta_5D'], df['Liq_Delta_30D'] = np.nan, np.nan

    df['Ratio_GO'] = df['GLD'] / df['USO'].replace(0, np.nan)
    df['Ratio_Risk'] = df['XLY'] / df['XLP'].replace(0, np.nan)
    df['Ratio_Br'] = df['SPY'] / df['RSP'].replace(0, np.nan)
    df['Ratio_HL'] = df['HYG'] / df['LQD'].replace(0, np.nan)
    df['Ratio_CG'] = df['CPER'] / df['GLD'].replace(0, np.nan)
    df['Ratio_SX'] = df['SOXX'] / df['SPY'].replace(0, np.nan)
    
    if 'US10Y' in df.columns and 'US2Y' in df.columns:
        df['Spread_10_2'] = df['US10Y'] - df['US2Y']
    else:
        df['Spread_10_2'] = np.nan

    metrics_for_zscore = ['SKEW', 'MOVE', 'P_C', 'DIX', 'GEX', 'DXY', 'Ratio_GO']
    for metric in metrics_for_zscore:
        if metric in df.columns:
            df[f'Z_{metric}'] = calculate_rolling_zscore(df[metric])

    return df


# ==========================================
# FASE 3: UI RENDERING (STREAMLIT)
# ==========================================
def render_metric_zscore(label, raw_val, z_val, invert_logic=False):
    if pd.isna(raw_val) or pd.isna(z_val):
        return st.metric(label, "N/D", "Dati mancanti")
        
    if not invert_logic:
        status, color = ("🔴 ECCESSO +", "inverse") if z_val > 1.5 else (("🟢 ECCESSO -", "normal") if z_val < -1.5 else ("⚪ NEUTRO", "off"))
    else:
        status, color = ("🟢 ECCESSO +", "normal") if z_val > 1.5 else (("🔴 ECCESSO -", "inverse") if z_val < -1.5 else ("⚪ NEUTRO", "off"))

    val_str = f"{raw_val:,.1f}" if raw_val > 10 else f"{raw_val:.2f}"
    st.metric(label, val_str, f"Z: {z_val:+.1f} | {status}", delta_color=color)

def render_page1():
    st.title("🌐 Macro Intelligence & Liquidità Fed")
    
    col_btn, _ = st.columns([1, 3])
    if col_btn.button("🔄 SINCRONIZZA FLUSSI EOD AUTOMATICI"):
        with st.spinner("Estrazione dati in corso..."):
            sync_macro_database()
            st.rerun()

    if not os.path.exists(DB_FILE):
        sync_macro_database()

    df_raw = pd.read_csv(DB_FILE)
    if df_raw.empty:
        st.error("Database vuoto. Sincronizzare i flussi.")
        return

    df = apply_math_engine(df_raw)
    last = df.iloc[-1]

    liq_30d = last.get('Liq_Delta_30D', np.nan)
    if not pd.isna(liq_30d):
        is_qe = liq_30d >= 0
        qe_color = "#10b981" if is_qe else "#ef4444"
        qe_status = "QUANTITATIVE EASING" if is_qe else "QUANTITATIVE TIGHTENING"
        st.markdown(
            f"""
            <div style="background: rgba(15,23,42,0.95); border: 2px solid {qe_color}; padding: 14px 18px; border-radius: 10px; margin-bottom: 15px;">
                <h4 style="margin: 0; color: #f8fafc;">🏛️ FED REGIME: {qe_status} ({liq_30d:+.2f}% 30D)</h4>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("---")
    st.subheader("🚦 Monitor Tensioni (Z-Score Storico)")
    
    r1, r2 = st.columns(6), st.columns(6)

    with r1[0]: render_metric_zscore("DIX", last.get('DIX'), last.get('Z_DIX'), invert_logic=True)
    with r1[1]: render_metric_zscore("GEX", last.get('GEX'), last.get('Z_GEX'), invert_logic=True)
    with r1[2]: render_metric_zscore("P/C RATIO", last.get('P_C'), last.get('Z_P_C'))
    with r1[3]: render_metric_zscore("SKEW", last.get('SKEW'), last.get('Z_SKEW'))
    with r1[4]: render_metric_zscore("MOVE", last.get('MOVE'), last.get('Z_MOVE'))
    
    d_liq = last.get('Liq_Delta_5D', np.nan)
    r1[5].metric("Δ LIQ. 5D", f"{d_liq:.2f}%" if not pd.isna(d_liq) else "N/D", "Flow", delta_color="off")

    with r2[0]: render_metric_zscore("DXY", last.get('DXY'), last.get('Z_DXY'))
    with r2[1]: render_metric_zscore("GOLD/OIL", last.get('Ratio_GO'), last.get('Z_Ratio_GO'))
    
    cg_val = last.get('Ratio_CG', np.nan)
    r2[2].metric("COPPER/GOLD", f"{cg_val:.3f}" if not pd.isna(cg_val) else "N/D", "Macro", delta_color="off")
    
    sp_10_2 = last.get('Spread_10_2', np.nan)
    r2[3].metric("SPREAD 10-2", f"{sp_10_2:+.2f}%" if not pd.isna(sp_10_2) else "N/D", "Curve", delta_color="off")
    
    bdry_val = last.get('BDRY', np.nan)
    r2[4].metric("BALTIC DRY", f"${bdry_val:.2f}" if not pd.isna(bdry_val) else "N/D", "Cargo", delta_color="off")
    
    soxx_val = last.get('Ratio_SX', np.nan)
    r2[5].metric("SEMI/SPY", f"{soxx_val:.2f}" if not pd.isna(soxx_val) else "N/D", "Tech", delta_color="off")

    st.markdown("---")
    st.subheader("📊 Analisi Strutturale")
    
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("#### Liquidità Netta Fed vs Bitcoin")
        df_plot = df.dropna(subset=['Data', 'Net_Liquidity'])
        if not df_plot.empty:
            fig_btc = go.Figure()
            fig_btc.add_trace(go.Scatter(x=df_plot['Data'], y=df_plot['Net_Liquidity'], name="Net Liq", fill='tozeroy', line=dict(color='#00CC96')))
            if 'BTC' in df_plot.columns and not df_plot['BTC'].isna().all():
                fig_btc.add_trace(go.Scatter(x=df_plot['Data'], y=df_plot['BTC'], name="BTC", yaxis="y2", line=dict(color='#f59e0b', width=2)))
                fig_btc.update_layout(yaxis2=dict(title="BTC ($)", overlaying="y", side="right", showgrid=False))
            fig_btc.update_layout(template="plotly_dark", height=320, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_btc, use_container_width=True)
            
    with g2:
        st.markdown("#### Z-Score SKEW (Rischio Coda)")
        df_skew = df.dropna(subset=['Data', 'Z_SKEW'])
        if not df_skew.empty:
            fig_skew = px.bar(df_skew.tail(252), x="Data", y="Z_SKEW", color="Z_SKEW", color_continuous_scale="RdYlGn_r")
            fig_skew.add_hline(y=2.0, line_dash="dash", line_color="red")
            fig_skew.add_hline(y=-2.0, line_dash="dash", line_color="green")
            fig_skew.update_layout(template="plotly_dark", height=320, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_skew, use_container_width=True)
