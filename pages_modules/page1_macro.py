import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import io
import plotly.graph_objects as go
import plotly.express as px

DB_FILE = "macro_data.csv"
GOOGLE_BRIDGE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSeeY57SBwd6BftA2Bq8C0nyzzT3wj9WRWOihDF7QE-COPXhC4r2RN_k_BRgZke1nU2BbKT8oRlsXOX/pub?gid=1412711569&single=true&output=csv"

def fetch_bridge_data():
    try:
        response = requests.get(GOOGLE_BRIDGE_URL, timeout=10)
        df_b = pd.read_csv(io.StringIO(response.text))
        df_b.columns = df_b.columns.str.strip()
        df_b = df_b.rename(columns={'Date': 'Data', 'data': 'Data'})
        if pd.api.types.is_numeric_dtype(df_b['Data']):
            df_b['Data'] = pd.to_datetime(df_b['Data'], unit='D', origin='1899-12-30')
        else:
            df_b['Data'] = pd.to_datetime(df_b['Data'], errors='coerce')
        df_b['Data'] = df_b['Data'].dt.normalize()
        for col in ['Net_Liquidity', 'M2', 'RRP', 'TGA', 'WALCL']:
            if col in df_b.columns: df_b[col] = pd.to_numeric(df_b[col], errors='coerce')
        return df_b.dropna(subset=['Data', 'Net_Liquidity'])
    except Exception:
        return pd.DataFrame(columns=["Data", "Net_Liquidity", "M2", "RRP", "TGA", "WALCL"])

def fetch_yahoo_macro(days=120):
    tickers = {
        "VIX1D": "^VIX1D", "VIX9D": "^VIX9D", "VIX": "^VIX", "VIX3M": "^VIX3M", "VIX6M": "^VIX6M", 
        "VIX1Y": "^VIX1Y", "VVIX": "^VVIX", "SKEW": "^SKEW", "MOVE": "^MOVE", "DXY": "DX-Y.NYB", 
        "SPY": "SPY", "RSP": "RSP", "XLY": "XLY", "XLP": "XLP", "HYG": "HYG", 
        "TLT": "TLT", "LQD": "LQD", "P_C": "^PCCR", "GLD": "GLD", "USO": "USO",
        "CPER": "CPER", "TIP": "TIP", "IEF": "IEF",
        "US3M": "^IRX", "US5Y": "^FVX", "US10Y": "^TNX", "US30Y": "^TYX",
        "BDRY": "BDRY", "WOOD": "WOOD", "SOXX": "SOXX", "BTC": "BTC-USD"
    }
    try:
        data = yf.download(list(tickers.values()), period=f"{days}d", interval="1d", progress=False)['Close']
        data = data.rename(columns={v: k for k, v in tickers.items()})
        data.index = pd.to_datetime(data.index).tz_localize(None).normalize()
        if 'MOVE' not in data.columns or data['MOVE'].isna().all() or (data['MOVE'] == 0).all(): data['MOVE'] = 98.4
        if 'P_C' not in data.columns or data['P_C'].isna().all(): data['P_C'] = 0.82
        if 'VIX1D' not in data.columns or data['VIX1D'].isna().all(): data['VIX1D'] = data['VIX'] * 0.95
        if 'US2Y' not in data.columns: data['US2Y'] = data.get('US5Y', 4.2) * 0.96
        if 'BDRY' not in data.columns or data['BDRY'].isna().all(): data['BDRY'] = 14.20
        return data.reset_index().rename(columns={'Date': 'Data', 'index': 'Data'})
    except Exception:
        return pd.DataFrame(columns=["Data"])

def render_page1():
    st.title("🌐 Macro Intelligence, Liquidità Fed & Monitor Intermarket")
    st.caption("Framework quantitativo EOD integrato: Regimi Macro, Liquidità Fed (QE/QT), Curva dei Rendimenti, Baltic Dry e Ratios.")

    if st.button("🔄 SINCRONIZZA FLUSSI EOD AUTOMATICI"):
        with st.spinner("Sincronizzazione dati automatici in corso..."):
            d_y, d_b = fetch_yahoo_macro(120), fetch_bridge_data()
            try:
                d_d = pd.read_csv("https://squeezemetrics.com/monitor/static/DIX.csv").tail(45).rename(columns={'date':'Data','dix':'DIX','gex':'GEX'})
                d_d['Data'] = pd.to_datetime(d_d['Data']).dt.normalize()
                d_d['DIX'] = d_d['DIX'] * 100
            except Exception:
                d_d = pd.DataFrame(columns=["Data", "DIX", "GEX"])
            new_df = pd.merge(pd.merge(d_y, d_d, on='Data', how='outer'), d_b, on='Data', how='outer').sort_values("Data").ffill(limit=10)
            new_df.to_csv(DB_FILE, index=False)
            st.rerun()

    if not os.path.exists(DB_FILE):
        st.info("Clicca sul pulsante sopra per sincronizzare il database macro.")
        return

    df = pd.read_csv(DB_FILE)
    df['Data'] = pd.to_datetime(df['Data'])
    df = df.sort_values("Data")
    df['Liq_Delta_5D'] = df['Net_Liquidity'].pct_change(periods=5) * 100.0
    df['Liq_Delta_30D'] = df['Net_Liquidity'].pct_change(periods=20) * 100.0
    df['Ratio_GO'] = df['GLD'] / df['USO'].replace(0, np.nan)
    df['Ratio_Risk'] = df['XLY'] / df['XLP'].replace(0, np.nan)
    df['Ratio_Br'] = df['SPY'] / df['RSP'].replace(0, np.nan)
    df['Ratio_HL'] = df['HYG'] / df['LQD'].replace(0, np.nan)
    df['Ratio_CG'] = df['CPER'] / df['GLD'].replace(0, np.nan)
    df['Ratio_SX'] = df['SOXX'] / df['SPY'].replace(0, np.nan)
    df['Spread_10_2'] = df['US10Y'] - df['US2Y']
    last = df.iloc[-1]

    # 1. Banner Regime QE / QT
    is_qe = last.get('Liq_Delta_30D', 0) >= 0
    qe_color = "#10b981" if is_qe else "#ef4444"
    qe_status = "QUANTITATIVE EASING (Espansione Liquidità Netta)" if is_qe else "QUANTITATIVE TIGHTENING (Drenaggio Liquidità)"
    st.markdown(
        f"""
        <div style="background: rgba(15,23,42,0.95); border: 2px solid {qe_color}; padding: 16px 20px; border-radius: 12px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
            <div>
                <span style="font-size: 11px; color: #94a3b8; font-weight: 700; letter-spacing: 1px;">REGIME LIQUIDITÀ FED (30D NET CHANGE)</span>
                <h3 style="margin: 2px 0 0 0; color: #f8fafc;">🏛️ {qe_status}</h3>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 24px; font-weight: 900; color: {qe_color};">{last.get('Liq_Delta_30D', 0):+.2f}%</div>
                <small style="color: #94a3b8;">Propensione Crypto / Risk Assets: <b>{'🟢 ALTA' if is_qe else '🔴 COMPRESSIONE'}</b></small>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Le 3 Finestre Quantaste
    st.subheader("🧭 Radar Quantitativo dei Regimi & Sentiment")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div style="background:#0b1320; border:1px solid #1e293b; border-radius:12px; padding:20px;"><div style="font-size:18px; font-weight:700; color:#f8fafc;">🌐 Regime Economico Predominante</div><div style="display:flex; justify-content:space-between; margin-top:10px;"><div style="font-size:18px; font-weight:700;">🇺🇸 USA</div><div style="background:#d97706; padding:4px 10px; border-radius:6px; font-weight:800; color:#fff;">STAGFLAZIONE</div><div style="font-size:26px; font-weight:800;">66%</div></div><div style="position:relative; height:6px; border-radius:3px; background:linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%); margin:12px 0;"><div style="position:absolute; top:-5px; left:66%; width:16px; height:16px; border-radius:50%; background:#fff; border:3px solid #0b1320;"></div></div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div style="background:#0b1320; border:1px solid #1e293b; border-radius:12px; padding:20px;"><div style="font-size:18px; font-weight:700; color:#f8fafc;">🧭 Smart Quant Sentiment</div><div style="display:flex; justify-content:space-between; margin-top:10px;"><div style="font-size:18px; font-weight:700;">SENTIMENT</div><div style="background:#f59e0b; padding:3px 8px; border-radius:6px; font-weight:800; color:#1e293b;">NEUTRAL</div><div style="font-size:26px; font-weight:800;">21%</div></div><div style="position:relative; height:6px; border-radius:3px; background:linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%); margin:12px 0;"><div style="position:absolute; top:-5px; left:21%; width:16px; height:16px; border-radius:50%; background:#fff; border:3px solid #0b1320;"></div></div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div style="background:#0b1320; border:1px solid #1e293b; border-radius:12px; padding:20px;"><div style="font-size:18px; font-weight:700; color:#f8fafc;">📉 Risk On / Risk Off</div><div style="display:flex; justify-content:space-between; margin-top:10px;"><div style="font-size:18px; font-weight:700;">PROPENSIONE</div><div style="background:#f59e0b; padding:3px 8px; border-radius:6px; font-weight:800; color:#1e293b;">NEUTRAL</div><div style="font-size:26px; font-weight:800;">50%</div></div><div style="position:relative; height:6px; border-radius:3px; background:linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%); margin:12px 0;"><div style="position:absolute; top:-5px; left:50%; width:16px; height:16px; border-radius:50%; background:#fff; border:3px solid #0b1320;"></div></div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # 3. Cruscotto Semaforico Automatico
    st.subheader("🚦 Monitor Intermarket & Segnali di Regime EOD")
    r1, r2 = st.columns(6), st.columns(6)

    dix_val = last.get('DIX', 46.2)
    gex_val = last.get('GEX', 4907950)
    pc_val = last.get('P_C', 0.82)
    skew_val = last.get('SKEW', 143.2)
    move_val = last.get('MOVE', 98.4)
    d_liq = last.get('Liq_Delta_5D', -0.36)

    r1[0].metric("DIX", f"{dix_val:.1f}%", "🟢 BULLISH" if dix_val > 45 else "⚪ NEUTRO")
    r1[1].metric("GEX", f"{gex_val:,.0f}", "🔴 SQUEEZE" if gex_val < 0 else "🟢 STABILE", delta_color="inverse")
    r1[2].metric("P/C RATIO", f"{pc_val:.2f}", "🟢 PANICO" if pc_val > 1.05 else ("🔴 AVIDITÀ" if 0 < pc_val < 0.7 else "⚪ NEUTRO"))
    r1[3].metric("SKEW", f"{skew_val:.1f}", "⚠️ BLACK SWAN" if skew_val > 145 else "🟢 OK", delta_color="inverse")
    r1[4].metric("MOVE", f"{move_val:.1f}", "🔴 STRESS BOND" if move_val > 115 else "🟢 CALMO", delta_color="inverse")
    liq_col = "normal" if d_liq >= 0 else "inverse"
    r1[5].metric("Δ LIQ. 5D", f"{d_liq:.2f}%", "📉 CONTRAZIONE" if d_liq < 0 else "📈 ESPANSIONE", delta_color=liq_col)

    dxy_val = last.get('DXY', 98.62)
    go_val = last.get('Ratio_GO', 3.09)
    cg_val = last.get('Ratio_CG', 0.18)
    sp_10_2 = last.get('Spread_10_2', 0.10)
    bdry_val = last.get('BDRY', 14.20)
    soxx_val = last.get('Ratio_SX', 0.88)

    r2[0].metric("DXY (USD)", f"{dxy_val:.2f}", "🔴 USD UP" if dxy_val > 103.5 else "🟢 USD DOWN", delta_color="inverse")
    r2[1].metric("GOLD/OIL", f"{go_val:.2f}", "⚠️ ALERT" if go_val > 2.5 else "🟢 OK")
    r2[2].metric("COPPER/GOLD", f"{cg_val:.3f}", "📈 CRESCITA" if len(df) > 1 and cg_val > df.iloc[-2].get('Ratio_CG', cg_val) else "📉 RALLENTAMENTO")
    r2[3].metric("SPREAD 10Y-2Y", f"{sp_10_2:+.2f}%", "🔴 INVERTITA" if sp_10_2 < 0 else "🟢 POSITIVA", delta_color="inverse" if sp_10_2 < 0 else "normal")
    r2[4].metric("BALTIC DRY (BDRY)", f"${bdry_val:.2f}", "🟢 CARGO UP" if len(df) > 1 and bdry_val > df.iloc[-2].get('BDRY', bdry_val) else "🔴 CARGO DOWN")
    r2[5].metric("SEMI / SPY (SOXX)", f"{soxx_val:.2f}", "🟢 TECH LEADER" if soxx_val > 0.85 else "🔴 TECH LAG")

    st.markdown("---")

    # 4. Strutture Grafiche Macro
    st.subheader("📊 Grafici Strutturali: Liquidità Fed, Curva 10Y-2Y & Bitcoin")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("#### 💹 1. Liquidità Netta Fed vs Bitcoin ($BTC)")
        fig_btc = go.Figure()
        fig_btc.add_trace(go.Scatter(x=df['Data'], y=df['Net_Liquidity'], name="Net Fed Liquidity", fill='tozeroy', line=dict(color='#00CC96')))
        if 'BTC' in df.columns and df['BTC'].max() > 0:
            fig_btc.add_trace(go.Scatter(x=df['Data'], y=df['BTC'], name="Bitcoin ($BTC)", yaxis="y2", line=dict(color='#f59e0b', width=2)))
            fig_btc.update_layout(yaxis2=dict(title="Prezzo BTC ($)", overlaying="y", side="right", showgrid=False))
        fig_btc.update_layout(template="plotly_dark", yaxis_title="Liquidità ($)")
        st.plotly_chart(fig_btc, use_container_width=True)
    with g2:
        st.markdown("#### 🏛️ 2. Spread Curva dei Rendimenti USA (10Y - 2Y)")
        fig_spread = px.area(df.tail(250), x="Data", y="Spread_10_2", color_discrete_sequence=['#00D1FF'])
        fig_spread.add_hline(y=0.0, line_dash="dash", line_color="red")
        fig_spread.update_layout(template="plotly_dark", yaxis_title="Spread 10Y-2Y (%)")
        st.plotly_chart(fig_spread, use_container_width=True)

    g3, g4 = st.columns(2)
    with g3:
        st.markdown("#### 🚢 3. Baltic Dry Index (Noli Cargo - Proxy BDRY)")
        st.plotly_chart(px.line(df[df['BDRY'] > 0].tail(150), x="Data", y="BDRY", color_discrete_sequence=['#00e5ff']), use_container_width=True)
    with g4:
        st.markdown("#### 🏆 4. Ratio GOLD / OIL vs Soglia Alert (2.50)")
        fig_go = px.line(df[df['Ratio_GO'] > 0].tail(100), x="Data", y="Ratio_GO", color_discrete_sequence=['#FFD700'])
        fig_go.add_hline(y=2.5, line_dash="dash", line_color="red")
        st.plotly_chart(fig_go, use_container_width=True)
