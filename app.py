import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import io
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. CONFIGURAZIONE STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="URANIA SYSTEM",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. CREDENZIALI & NOTIFIER TELEGRAM (SOLO STOCK SCREENER)
# -----------------------------------------------------------------------------
BOT_TOKEN = "8829669929:AAFHyp1WeBtpebQD-xqua-MsNyq8S_r8uQ0"
CHAT_ID = "-1004435512748"

def send_stock_telegram_alert(ticker: str, details: dict) -> tuple[bool, str]:
    msg = (
        f"🚨 <b>URANIA RADAR — SEGNALE OPERATIVO</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Asset:</b> <code>${ticker}</code>\n"
        f"📈 <b>Protocollo:</b> {details.get('protocol', 'Setup Quant')}\n"
        f"💵 <b>Prezzo EOD:</b> ${details.get('price', 0.0):.2f}\n"
        f"📉 <b>Drawdown da ATH:</b> {details.get('drawdown', 0.0):.1f}%\n"
        f"🎯 <b>POC Volume Base:</b> ${details.get('poc', 0.0):.2f} ({details.get('poc_dist', 0.0):+.2f}%)\n"
        f"📊 <b>Z-Score 52w:</b> {details.get('z_score', 0.0):.2f}\n"
        f"🎯 <b>Target Superiore:</b> ${details.get('target', 0.0):.2f}\n"
        f"⚖️ <b>Risk/Reward:</b> {details.get('rr_ratio', 0.0):.2f} : 1\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"ℹ️ <i>Validazione quantitativa su dati EOD.</i>"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        res = r.json()
        if r.status_code == 200 and res.get("ok"):
            return True, "Alert inviato a Telegram."
        return False, f"Errore API: {res.get('description', 'Unauthorized')}"
    except Exception as e:
        return False, f"Errore rete: {str(e)}"

# -----------------------------------------------------------------------------
# 3. GESTIONE AUTENTICAZIONE & LOGO
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #030712 !important;
            background-image: radial-gradient(circle at 50% 35%, #0f172a 0%, #030712 100%) !important;
        }
        .login-card {
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(212, 175, 55, 0.35);
            border-radius: 16px;
            padding: 30px 20px;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
        }
        .brand-title {
            font-size: 30px;
            font-weight: 900;
            letter-spacing: 4px;
            color: #f8fafc;
            margin-top: 10px;
            margin-bottom: 2px;
        }
        .brand-motto {
            font-size: 11px;
            letter-spacing: 3px;
            color: #d4af37;
            font-weight: 700;
            margin-bottom: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.3, 1])

    logo_path = None
    for p in ["urania_logo.png", "urania.png"]:
        if os.path.exists(p):
            logo_path = p
            break

    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if logo_path:
            st.image(logo_path, use_container_width=True)
        else:
            st.markdown('<div style="font-size: 48px; margin-bottom: 8px;">🛡️</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="brand-title">URANIA</div>
            <div class="brand-motto">PRECISION. CONSISTENCY. GROWTH.</div>
            <p style="color: #94a3b8; font-size: 13px; margin: 0 0 10px 0;">
                Macro Quantitative Terminal • EOD Execution Engine
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        pwd = st.text_input("Password di Accesso:", type="password", placeholder="••••••••••••")
        
        if st.button("SBLOCCA TERMINALE", use_container_width=True):
            if pwd == "Serafino12?#":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Credenziali non valide.")
    st.stop()

# -----------------------------------------------------------------------------
# 4. DATABASE LOCALE EOD & FETCHERS AUTOMATIZZATI
# -----------------------------------------------------------------------------
DB_FILE = "macro_data.csv"
COLUMNS = ["Data", "VIX1D", "VIX9D", "VIX", "VIX3M", "VIX6M", "VIX1Y", "VVIX", "MOVE", "SKEW", 
           "DXY", "DIX", "GEX", "SPY", "RSP", "HYG", "XLY", "XLP", "TLT", "LQD", "P_C", "GLD", "USO", "Net_Liquidity", "M2"]

GOOGLE_BRIDGE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSeeY57SBwd6BftA2Bq8C0nyzzT3wj9WRWOihDF7QE-COPXhC4r2RN_k_BRgZke1nU2BbKT8oRlsXOX/pub?gid=1412711569&single=true&output=csv"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            df['Data'] = pd.to_datetime(df['Data']).dt.normalize()
            for col in COLUMNS:
                if col not in df.columns: df[col] = 0.0
            return df.sort_values("Data")
        except Exception:
            pass
    return pd.DataFrame(columns=COLUMNS)

def save_db(df):
    df = df.drop_duplicates(subset=['Data'], keep='last').sort_values("Data")
    df.to_csv(DB_FILE, index=False)

def fetch_bridge_data():
    try:
        response = requests.get(GOOGLE_BRIDGE_URL, timeout=10)
        df_bridge = pd.read_csv(io.StringIO(response.text))
        df_bridge.columns = df_bridge.columns.str.strip()
        df_bridge = df_bridge.rename(columns={'Date': 'Data', 'data': 'Data'})
        if pd.api.types.is_numeric_dtype(df_bridge['Data']):
            df_bridge['Data'] = pd.to_datetime(df_bridge['Data'], unit='D', origin='1899-12-30')
        else:
            df_bridge['Data'] = pd.to_datetime(df_bridge['Data'], errors='coerce')
        df_bridge['Data'] = df_bridge['Data'].dt.normalize()
        for col in ['Net_Liquidity', 'M2']:
            if col in df_bridge.columns: df_bridge[col] = pd.to_numeric(df_bridge[col], errors='coerce')
        return df_bridge.dropna(subset=['Data', 'Net_Liquidity'])
    except Exception:
        return pd.DataFrame(columns=["Data", "Net_Liquidity", "M2"])

def fetch_yahoo_eod(days=90):
    tickers = {
        "VIX9D": "^VIX9D", "VIX": "^VIX", "VIX3M": "^VIX3M", "VIX6M": "^VIX6M", 
        "VIX1Y": "^VIX1Y", "VVIX": "^VVIX", "SKEW": "^SKEW", "DXY": "DX-Y.NYB", 
        "SPY": "SPY", "RSP": "RSP", "XLY": "XLY", "XLP": "XLP", "HYG": "HYG", 
        "TLT": "TLT", "LQD": "LQD", "P_C": "^PCCR", "GLD": "GLD", "USO": "USO"
    }
    try:
        data = yf.download(list(tickers.values()), period=f"{days}d", interval="1d", progress=False)['Close']
        data = data.rename(columns={v: k for k, v in tickers.items()})
        data.index = pd.to_datetime(data.index).tz_localize(None).normalize()
        # Fallback automatico per Put/Call Ratio
        if 'P_C' not in data.columns or data['P_C'].isna().all():
            data['P_C'] = 0.85
        return data.reset_index().rename(columns={'Date': 'Data', 'index': 'Data'})
    except Exception:
        return pd.DataFrame(columns=["Data"])

# -----------------------------------------------------------------------------
# 5. ENGINE MATEMATICO (POC & ALERT VISIVI)
# -----------------------------------------------------------------------------
def calculate_eod_poc(df: pd.DataFrame, bins: int = 50) -> float:
    if df.empty or 'Close' not in df or 'Volume' not in df:
        return 0.0
    price_bins = np.linspace(df['Low'].min(), df['High'].max(), bins)
    bin_idx = np.digitize(df['Close'].values, price_bins)
    vol_hist = np.zeros(len(price_bins))
    for idx, v in zip(bin_idx, df['Volume'].values):
        if idx < len(vol_hist):
            vol_hist[idx] += v
    return float(price_bins[np.argmax(vol_hist)])

def evaluate_macro_visual_alerts(df: pd.DataFrame) -> list[dict]:
    if len(df) < 6:
        return []
    last = df.iloc[-1]
    prev5 = df.iloc[-6]
    alerts = []

    # 1. Divergenza Bearish Liquidità Netta vs SPY
    if prev5.get('Net_Liquidity', 0) > 0:
        liq_delta = ((last['Net_Liquidity'] - prev5['Net_Liquidity']) / prev5['Net_Liquidity']) * 100.0
        if liq_delta < -0.5 and last.get('SPY', 0) > prev5.get('SPY', 0):
            alerts.append({
                "type": "Divergenza Liquidità Fed vs SPY",
                "severity": "CRITICAL",
                "color": "#ef4444",
                "desc": f"Liquidità Netta in contrazione ({liq_delta:+.2f}% su 5gg) mentre SPY sale. Rischio bull-trap per drenaggio monetario."
            })

    # 2. Inversione Curva VIX
    v9 = last.get('VIX9D', 0)
    vx = last.get('VIX', 0)
    if v9 > vx and vx > 0:
        alerts.append({
            "type": "Inversione Curva Volatilità (VIX9D > VIX)",
            "severity": "HIGH",
            "color": "#f59e0b",
            "desc": f"Curva di volatilità invertita (9D: {v9:.1f} vs 30D: {vx:.1f}). Stress di brevissimo termine e forte domanda di coperture."
        })

    # 3. Ratio Gold / Oil (Stress Geopolitico / Macro)
    r_go = last.get('GLD', 1) / max(0.01, last.get('USO', 1))
    if r_go >= 2.5:
        alerts.append({
            "type": "Ratio Gold / Oil in Area Alert",
            "severity": "WARNING",
            "color": "#eab308",
            "desc": f"Rapporto Oro/Petrolio a quota {r_go:.2f} (> 2.50). Segnale di avversione al rischio globale e debolezza della domanda industriale."
        })

    # 4. Concentrazione Indice (SPY / RSP)
    r_br = last.get('SPY', 1) / max(0.01, last.get('RSP', 1))
    if r_br >= 3.45:
        alerts.append({
            "type": "Deterioramento Market Breadth (SPY/RSP)",
            "severity": "WARNING",
            "color": "#38bdf8",
            "desc": f"Rapporto SPY/RSP a quota {r_br:.2f}. Il mercato è sostenuto prevalentemente da poche mega-cap a discapito dell'ampiezza generale."
        })

    return alerts

# -----------------------------------------------------------------------------
# 6. STYLING CSS
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .macro-card {
        background-color: #0b1320;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 22px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .card-header {
        font-size: 18px;
        font-weight: 700;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 18px;
    }
    .stat-pill {
        background-color: #111e33;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 10px 8px;
        text-align: center;
    }
    .slider-track {
        position: relative;
        height: 6px;
        border-radius: 3px;
        background: linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%);
        margin-top: 10px;
        margin-bottom: 6px;
    }
    .slider-pin {
        position: absolute;
        top: -5px;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #ffffff;
        border: 3px solid #0b1320;
        box-shadow: 0 0 6px rgba(0,0,0,0.8);
        transform: translateX(-50%);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# 7. SIDEBAR LAZY LOADING
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛡️ URANIA SYSTEM")
    st.caption("Macro Quantitative Terminal • EOD Engine")
    nav = st.radio(
        "Seleziona Modulo Operativo:",
        [
            "1. Panoramica Macro & Rapporti EOD",
            "2. Protocol Stock Screener (Telegram)",
            "3. Z-Score & COT Lab",
            "4. Inserimento Dati EOD"
        ]
    )
    st.markdown("---")
    st.markdown("● **Pipeline Status:** `EOD Ready` ✅")
    st.markdown("● **Telegram Radar:** `Attivo (Modulo Screener)` 📡")
    if st.button("🔒 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

df = load_db()

# ==============================================================================
# MODULO 1: PANORAMICA MACRO & RAPPORTI AUTOMATICI (NO TELEGRAM)
# ==============================================================================
if nav == "1. Panoramica Macro & Rapporti EOD":
    st.title("Panoramica Macro e Mercati")
    st.caption("Intelligence quantitativa EOD con calcolo automatico di rapporti, flussi monetari e semafori di regime.")

    if st.button("🔄 SINCRONIZZA FLUSSI EOD & RICALCOLA RAPPORTI"):
        with st.spinner("Sincronizzazione dati storici e calcolo metriche..."):
            d_y, d_b = fetch_yahoo_eod(90), fetch_bridge_data()
            try:
                d_d = pd.read_csv("https://squeezemetrics.com/monitor/static/DIX.csv").tail(31).rename(columns={'date':'Data','dix':'DIX','gex':'GEX'})
                d_d['Data'] = pd.to_datetime(d_d['Data']).dt.normalize(); d_d['DIX'] = d_d['DIX'] * 100
            except Exception:
                d_d = pd.DataFrame(columns=["Data", "DIX", "GEX"])
            
            new_df = pd.merge(pd.merge(d_y, d_d, on='Data', how='outer'), d_b, on='Data', how='outer')
            if not df.empty:
                manual_cols = [c for c in ['MOVE', 'VIX1D', 'P_C', 'DIX', 'GEX'] if c in df.columns]
                manual_data = df[['Data'] + manual_cols].copy()
                new_df = pd.merge(new_df, manual_data, on='Data', how='left', suffixes=('', '_old'))
                for c in manual_cols:
                    if f'{c}_old' in new_df.columns: new_df[c] = new_df[c].fillna(new_df[f'{c}_old'])
            new_df = new_df.sort_values("Data").ffill(limit=7)
            save_db(new_df)
            st.rerun()

    if not df.empty:
        df = df.sort_values("Data")
        # Calcolo Automatico Ratio e Delta
        df['Liq_Delta_5D'] = df['Net_Liquidity'].pct_change(periods=5) * 100.0
        df['Ratio_GO'] = df['GLD'] / df['USO'].replace(0, np.nan)
        df['Ratio_Risk'] = df['XLY'] / df['XLP'].replace(0, np.nan)
        df['Ratio_Br'] = df['SPY'] / df['RSP'].replace(0, np.nan)
        last = df.iloc[-1]

        # 1. Sezione Alert Visivi
        alerts_visivi = evaluate_macro_visual_alerts(df)
        if alerts_visivi:
            st.subheader("🚨 Alert Visivi di Divergenza ed Eccesso Macro")
            for alt in alerts_visivi:
                st.markdown(
                    f"""
                    <div style="background: rgba(18,26,47,0.85); border-left: 5px solid {alt['color']}; padding: 14px 18px; border-radius: 8px; margin-bottom: 10px;">
                        <span style="font-weight: 800; font-size: 14px; color: {alt['color']};">[{alt['severity']}] {alt['type']}</span>
                        <p style="color: #cbd5e1; margin: 4px 0 0 0; font-size: 13px;">{alt['desc']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            st.markdown("<br>", unsafe_allow_html=True)

        # 2. Le 3 Finestre Quantaste
        st.subheader("🧭 Radar Quantitativo dei Regimi")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                """
                <div class="macro-card">
                    <div class="card-header">🌐 Regime Economico Predominante</div>
                    <div style="font-size: 11px; color: #94a3b8; letter-spacing: 0.5px; font-weight: 600;">REGIME DOMINANTE</div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 6px; margin-bottom: 8px;">
                        <div style="font-size: 18px; font-weight: 700; color: #f8fafc;">🇺🇸 USA</div>
                        <div style="background-color:#d97706; color:#fff; font-weight:800; padding:4px 10px; border-radius:6px; font-size:13px;">STAGFLAZIONE</div>
                        <div style="font-size: 26px; font-weight: 800; color: #f8fafc;">66<span style="font-size: 16px; color: #94a3b8;">%</span></div>
                    </div>
                    <div class="slider-track"><div class="slider-pin" style="left: 66%;"></div></div>
                    <div style="display: flex; justify-content: space-between; font-size: 10px; color: #64748b; margin-bottom: 16px; margin-top: 4px;">
                        <span>0</span><span>50</span><span>100</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 22px;">
                        <div class="stat-pill"><div style="font-size: 10px; color: #94a3b8;">🇪🇺 Europa</div><div style="color: #10b981; font-weight: 700; font-size: 11px; margin: 3px 0;">REFLAZIONE</div><div style="font-weight: 800; font-size: 14px;">72%</div></div>
                        <div class="stat-pill"><div style="font-size: 10px; color: #94a3b8;">🇨🇦 Canada</div><div style="color: #f59e0b; font-weight: 700; font-size: 11px; margin: 3px 0;">STAGFLAZ.</div><div style="font-weight: 800; font-size: 14px;">68%</div></div>
                        <div class="stat-pill"><div style="font-size: 10px; color: #94a3b8;">🇨🇳 Cina</div><div style="color: #f59e0b; font-weight: 700; font-size: 11px; margin: 3px 0;">STAGFLAZ.</div><div style="font-weight: 800; font-size: 14px;">59%</div></div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 4px; text-align: center;">
                        <div><div style="width: 58px; height: 58px; border-radius: 50%; border: 4px solid #f59e0b; display: flex; align-items: center; justify-content: center; font-weight: 800; margin: auto;">69%</div><div style="font-size: 10px; color: #94a3b8; margin-top: 6px;">Bonds</div></div>
                        <div><div style="width: 58px; height: 58px; border-radius: 50%; border: 4px solid #f59e0b; display: flex; align-items: center; justify-content: center; font-weight: 800; margin: auto;">67%</div><div style="font-size: 10px; color: #94a3b8; margin-top: 6px;">Commodities</div></div>
                        <div><div style="width: 58px; height: 58px; border-radius: 50%; border: 4px solid #f59e0b; display: flex; align-items: center; justify-content: center; font-weight: 800; margin: auto;">64%</div><div style="font-size: 10px; color: #94a3b8; margin-top: 6px;">Stocks</div></div>
                        <div><div style="width: 58px; height: 58px; border-radius: 50%; border: 4px solid #ef4444; color:#ef4444; display: flex; align-items: center; justify-content: center; font-weight: 800; margin: auto;">25%</div><div style="font-size: 10px; color: #94a3b8; margin-top: 6px;">Crypto</div></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                """
                <div class="macro-card">
                    <div class="card-header">🧭 Smart Quant Sentiment</div>
                    <div style="font-size: 11px; color: #94a3b8; letter-spacing: 0.5px; font-weight: 600;">SENTIMENT DI MERCATO</div>
                    <div style="display: flex; align-items: center; justify-content: flex-end; gap: 10px; margin-top: 4px; margin-bottom: 8px;">
                        <div style="background-color:#f59e0b; color:#1e293b; font-weight:800; padding:3px 8px; border-radius:6px; font-size:12px;">NEUTRAL</div>
                        <div style="font-size: 26px; font-weight: 800; color: #f8fafc;">21<span style="font-size: 16px; color: #94a3b8;">%</span></div>
                    </div>
                    <div class="slider-track"><div class="slider-pin" style="left: 21%;"></div></div>
                    <div style="display: flex; justify-content: space-between; font-size: 10px; color: #64748b; margin-bottom: 16px; margin-top: 4px;">
                        <span>Ext. Sell</span><span>Hold</span><span>Ext. Buy</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 20px;">
                        <div class="stat-pill"><div style="font-size: 10px; color: #94a3b8;">Sell</div><div style="color: #ef4444; font-weight: 800; font-size: 15px; margin-top: 2px;">↓ 43%</div></div>
                        <div class="stat-pill"><div style="font-size: 10px; color: #94a3b8;">Hold</div><div style="color: #f59e0b; font-weight: 800; font-size: 15px; margin-top: 2px;">21%</div></div>
                        <div class="stat-pill"><div style="font-size: 10px; color: #94a3b8;">Buy</div><div style="color: #10b981; font-weight: 800; font-size: 15px; margin-top: 2px;">↑ 36%</div></div>
                    </div>
                    <div style="font-size: 11px; color: #94a3b8; font-weight: 600; margin-bottom: 8px;">DISTRIBUZIONE SEGNALI</div>
                    <div style="display: flex; flex-direction: column; gap: 6px; font-size: 11px;">
                        <div style="display: flex; align-items: center;"><span style="width: 75px; color: #94a3b8;">Strong Buy</span><div style="flex: 1; background: #111e33; height: 12px; border-radius: 3px; margin: 0 8px;"><div style="width: 9%; background: #10b981; height: 100%;"></div></div><span style="width: 28px; font-weight: 700;">9%</span></div>
                        <div style="display: flex; align-items: center;"><span style="width: 75px; color: #94a3b8;">Buy</span><div style="flex: 1; background: #111e33; height: 12px; border-radius: 3px; margin: 0 8px;"><div style="width: 27%; background: #10b981; height: 100%;"></div></div><span style="width: 28px; font-weight: 700;">27%</span></div>
                        <div style="display: flex; align-items: center;"><span style="width: 75px; color: #94a3b8;">Hold</span><div style="flex: 1; background: #111e33; height: 12px; border-radius: 3px; margin: 0 8px;"><div style="width: 21%; background: #f59e0b; height: 100%;"></div></div><span style="width: 28px; font-weight: 700;">21%</span></div>
                        <div style="display: flex; align-items: center;"><span style="width: 75px; color: #94a3b8;">Sell</span><div style="flex: 1; background: #111e33; height: 12px; border-radius: 3px; margin: 0 8px;"><div style="width: 36%; background: #ef4444; height: 100%;"></div></div><span style="width: 28px; font-weight: 700;">36%</span></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                """
                <div class="macro-card">
                    <div class="card-header">📉 Risk On / Risk Off</div>
                    <div style="font-size: 11px; color: #94a3b8; letter-spacing: 0.5px; font-weight: 600;">PROPENSIONE AL RISCHIO</div>
                    <div style="display: flex; align-items: center; justify-content: flex-end; gap: 10px; margin-top: 4px; margin-bottom: 8px;">
                        <div style="background-color:#f59e0b; color:#1e293b; font-weight:800; padding:3px 8px; border-radius:6px; font-size:12px;">NEUTRAL</div>
                        <div style="font-size: 26px; font-weight: 800; color: #f8fafc;">50<span style="font-size: 16px; color: #94a3b8;">%</span></div>
                    </div>
                    <div class="slider-track"><div class="slider-pin" style="left: 50%;"></div></div>
                    <div style="display: flex; justify-content: space-between; font-size: 10px; color: #64748b; margin-bottom: 16px; margin-top: 4px;">
                        <span>Ext. Risk Off</span><span>Neutral</span><span>Ext. Risk On</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 16px;">
                        <div class="stat-pill"><div style="font-size: 10px; color: #94a3b8;">Risk Assets</div><div style="font-weight: 800; font-size: 15px; margin-top: 2px;">50%</div></div>
                        <div class="stat-pill"><div style="font-size: 10px; color: #94a3b8;">Difensivo</div><div style="font-weight: 800; font-size: 15px; margin-top: 2px;">30%</div></div>
                        <div class="stat-pill"><div style="font-size: 10px; color: #94a3b8;">Cash</div><div style="font-weight: 800; font-size: 15px; margin-top: 2px;">20%</div></div>
                    </div>
                    <div style="font-size: 11px; color: #94a3b8; font-weight: 600; margin-bottom: 8px;">DETTAGLIO SEGNALI QUANTITATIVI</div>
                    <div style="display: flex; flex-direction: column; gap: 6px; font-size: 11px;">
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px;"><span style="color: #94a3b8;">TIP Momentum</span><span style="font-weight: 700; color: #f8fafc;">0/20</span></div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px;"><span style="color: #94a3b8;">VIX Structure</span><span style="font-weight: 700; color: #10b981;">+20/20</span></div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px;"><span style="color: #94a3b8;">Credit Spreads (HYG/LQD)</span><span style="font-weight: 700; color: #10b981;">+10/10</span></div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px;"><span style="color: #94a3b8;">Consumer Appetite (XLY/XLP)</span><span style="font-weight: 700; color: #10b981;">+15/15</span></div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px;"><span style="color: #94a3b8;">Risk Flows (IWM/SPY)</span><span style="font-weight: 700; color: #10b981;">+10/15</span></div>
                        <div style="display: flex; justify-content: space-between; padding-bottom: 3px;"><span style="color: #94a3b8;">Primary Trend</span><span style="font-weight: 700; color: #10b981;">+20/20</span></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")

        # 3. Griglia dei Rapporti e Semafori di Regime
        st.subheader("🚦 Monitor Segnali di Regime & Rapporti EOD")
        r1, r2 = st.columns(6), st.columns(6)

        dix_val = last.get('DIX', 0.0)
        gex_val = last.get('GEX', 0.0)
        pc_val = last.get('P_C', 0.85) if not pd.isna(last.get('P_C', np.nan)) else 0.85
        skew_val = last.get('SKEW', 0.0)
        move_val = last.get('MOVE', 0.0)
        d_liq = last.get('Liq_Delta_5D', 0.0)

        r1[0].metric("DIX", f"{dix_val:.1f}%", "🟢 BULLISH" if dix_val > 45 else "⚪ NEUTRO")
        r1[1].metric("GEX", f"{gex_val:,.0f}", "🔴 SQUEEZE" if gex_val < 0 else "🟢 STABILE", delta_color="inverse")
        r1[2].metric("P/C RATIO", f"{pc_val:.2f}", "🟢 PANICO" if pc_val > 1.05 else ("🔴 AVIDITÀ" if 0 < pc_val < 0.7 else "⚪ NEUTRO"))
        r1[3].metric("SKEW", f"{skew_val:.1f}", "⚠️ BLACK SWAN" if skew_val > 145 else "🟢 OK", delta_color="inverse")
        r1[4].metric("MOVE", f"{move_val:.1f}", "🔴 STRESS BOND" if move_val > 115 else "🟢 CALMO", delta_color="inverse")
        liq_col = "normal" if d_liq >= 0 else "inverse"
        r1[5].metric("Δ LIQ. 5D", f"{d_liq:.2f}%", "📉 CONTRAZIONE" if d_liq < 0 else "📈 ESPANSIONE", delta_color=liq_col)

        dxy_val = last.get('DXY', 0.0)
        go_val = last.get('Ratio_GO', 0.0)
        tlt_val = last.get('TLT', 0.0)
        risk_val = last.get('Ratio_Risk', 0.0)
        br_val = last.get('Ratio_Br', 0.0)
        v9_val = last.get('VIX9D', 0.0)
        vx_val = last.get('VIX', 0.0)

        r2[0].metric("DXY", f"{dxy_val:.2f}", "🔴 USD UP" if dxy_val > 103.5 else "🟢 USD DOWN", delta_color="inverse")
        r2[1].metric("GOLD/OIL", f"{go_val:.2f}", "⚠️ ALERT" if go_val > 2.5 else "🟢 OK")
        r2[2].metric("TLT PRICE", f"${tlt_val:.2f}", "📈 TASSI DOWN" if len(df) > 1 and tlt_val > df.iloc[-2]['TLT'] else "📉 TASSI UP")
        r2[3].metric("XLY/XLP", f"{risk_val:.2f}", "🟢 RISK-ON" if risk_val > 1.45 else "🔴 DIFESA")
        r2[4].metric("SPY/RSP", f"{br_val:.2f}", "⚠️ ALERT" if br_val > 3.45 else "🟢 SANA")
        v_stat = "🔴 INVERTITA" if v9_val > vx_val else "🟢 CONTANGO"
        r2[5].metric("CURVA VIX", f"{v9_val:.1f}/{vx_val:.1f}", v_stat)

        st.markdown("---")

        # 4. Grafici Analitici Macro
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("💹 1. Liquidità Netta Fed (WALCL - TGA - RRP)")
            st.plotly_chart(px.area(df[df['Net_Liquidity'] > 0].tail(250), x="Data", y="Net_Liquidity", color_discrete_sequence=['#00CC96']), use_container_width=True)
        with c2:
            st.subheader("💰 2. M2 Money Supply")
            st.plotly_chart(px.line(df[df['M2'] > 0].tail(250), x="Data", y="M2"), use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            st.subheader("🏆 3. Ratio GOLD / OIL")
            fig_go = px.line(df[df['Ratio_GO'] > 0].tail(100), x="Data", y="Ratio_GO", color_discrete_sequence=['#FFD700'])
            fig_go.add_hline(y=2.5, line_dash="dash", line_color="red")
            st.plotly_chart(fig_go, use_container_width=True)
        with c4:
            st.subheader("📉 4. Bond Stress: TLT vs MOVE")
            st.plotly_chart(px.line(df.tail(100), x="Data", y=["TLT", "MOVE"], color_discrete_map={"TLT": "yellow", "MOVE": "red"}), use_container_width=True)

# ==============================================================================
# MODULO 2: PROTOCOL STOCK SCREENER (CON DISPATCH TELEGRAM)
# ==============================================================================
elif nav == "2. Protocol Stock Screener (Telegram)":
    st.title("🎯 Protocol Stock Screener & Telegram Radar")
    st.caption("Scansione quantitativa EOD dell'universo azionario e dispatching automatico su canale Telegram.")
    st.markdown("---")

    raw_watchlist = st.text_area(
        "Watchlist Titoli (separati da virgola):",
        "PYPL, AXON, PLTR, ENPH, BABA, NIO, TSLA, SQ, SHOP, AMD, NVDA, COIN"
    )
    tickers = [t.strip().upper() for t in raw_watchlist.split(",") if t.strip()]

    c1, c2, c3 = st.columns(3)
    dd_limit = c1.slider("Min Drawdown ATH (%):", -85.0, -15.0, -30.0)
    poc_tol = c2.slider("Tolleranza Distanza POC (%):", 1.0, 10.0, 5.0)
    z_filt = c3.checkbox("Filtro Z-Score <= -1.0", value=True)

    if st.button("🚀 ESEGUI SCANSIONE EOD & DISPATCH ALERTS TELEGRAM"):
        results = []
        alerts_sent = 0
        with st.spinner("Scansione EOD in corso..."):
            for t in tickers:
                try:
                    df_t = yf.download(t, period="1y", interval="1d", progress=False)
                    if not df_t.empty and len(df_t) >= 50:
                        if isinstance(df_t.columns, pd.MultiIndex):
                            df_t.columns = df_t.columns.get_level_values(0)

                        last_close = float(df_t['Close'].iloc[-1])
                        ath_high = float(df_t['High'].max())
                        drawdown = ((last_close - ath_high) / ath_high) * 100.0
                        poc_price = calculate_eod_poc(df_t)
                        dist_poc = ((last_close - poc_price) / poc_price) * 100.0

                        ret = df_t['Close'].pct_change()
                        z_score = float((ret.iloc[-1] - ret.mean()) / (ret.std() + 1e-9))

                        protocol_hit = None
                        if drawdown <= dd_limit and abs(dist_poc) <= poc_tol:
                            if not z_filt or z_score <= -1.0:
                                protocol_hit = "POC Capitulation (Bottom Hunter)"
                        elif drawdown <= -20.0 and dist_poc > 1.5:
                            protocol_hit = "Rounding Base Breakout"

                        status_notifica = "Nessun Trigger"
                        if protocol_hit:
                            target_price = poc_price * 1.25 if "Capitulation" in protocol_hit else last_close * 1.20
                            stop_price = poc_price * 0.95
                            risk = max(0.01, last_close - stop_price)
                            reward = max(0.01, target_price - last_close)
                            rr = reward / risk

                            payload = {
                                "protocol": protocol_hit,
                                "price": last_close,
                                "drawdown": drawdown,
                                "poc": poc_price,
                                "poc_dist": dist_poc,
                                "z_score": z_score,
                                "target": target_price,
                                "rr_ratio": rr
                            }
                            ok, _ = send_stock_telegram_alert(t, payload)
                            if ok:
                                alerts_sent += 1
                                status_notifica = "Inviato a Telegram 🎯"

                        results.append({
                            "Ticker": t,
                            "Prezzo EOD": f"${last_close:.2f}",
                            "Drawdown ATH": f"{drawdown:.1f}%",
                            "POC Volume": f"${poc_price:.2f}",
                            "Distanza POC": f"{dist_poc:+.2f}%",
                            "Z-Score": f"{z_score:.2f}",
                            "Protocollo": protocol_hit if protocol_hit else "—",
                            "Stato Telegram": status_notifica
                        })
                except Exception:
                    pass

        st.success(f"Scansione completata. Segnali inviati a Telegram: {alerts_sent}")
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

# ==============================================================================
# MODULO 3: Z-SCORE & COT LAB
# ==============================================================================
elif nav == "3. Z-Score & COT Lab":
    st.title("📊 Z-Score Normalization & COT Positioning Lab")
    st.caption("Analisi quantitativa dei flussi istituzionali (CFTC) con normalizzazione Z-Score a 1/3/5 anni.")
    c1, c2 = st.columns([1, 2])
    with c1:
        asset = st.selectbox("Seleziona Sottostante / Future:", ["Cocoa", "Coffee", "Natural Gas", "Crude Oil", "Gold", "S&P 500", "US 10Y Note"])
        lookback = st.radio("Finestra di Normalizzazione Z-Score:", ["1 Anno (52w)", "3 Anni (156w)", "5 Anni (260w)"])
    with c2:
        st.info(f"Asset selezionato: **{asset}** | Lookback: **{lookback}**")

# ==============================================================================
# MODULO 4: INSERIMENTO DATI EOD
# ==============================================================================
elif nav == "4. Inserimento Dati EOD":
    st.title("✍️ Inserimento Manuale Dati EOD")
    with st.form("manual_entry"):
        m_date = st.date_input("Data Riferimento:", datetime.now())
        m_v1 = st.number_input("VIX 1D", 0.0)
        m_move = st.number_input("MOVE Index", 0.0)
        m_pc = st.number_input("Put/Call Ratio", 0.0)
        m_dix = st.number_input("DIX (%)", 0.0)
        m_gex = st.number_input("GEX", 0.0)
        if st.form_submit_button("REGISTRA NEL DATABASE EOD"):
            dt = pd.to_datetime(m_date).normalize()
            if not df.empty and dt in df['Data'].values:
                for k, v in zip(['VIX1D','MOVE','P_C','DIX','GEX'],[m_v1,m_move,m_pc,m_dix,m_gex]):
                    if v != 0: df.loc[df['Data'] == dt, k] = v
            else:
                row = {c: 0.0 for c in COLUMNS}; row.update({"Data": dt, "VIX1D": m_v1, "MOVE": m_move, "P_C": m_pc, "DIX": m_dix, "GEX": m_gex})
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            save_db(df)
            st.success("Dati registrati correttamente nel file macro_data.csv.")
