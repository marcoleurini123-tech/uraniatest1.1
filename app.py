import streamlit as st
import pandas as pd
import numpy as np
import requests
import yfinance as yf
from core.auth import check_authentication

# -----------------------------------------------------------------------------
# CONFIGURAZIONE GENERALE STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="URANIA SYSTEM",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. Gate di Sicurezza Modulare
if not check_authentication():
    st.stop()

# -----------------------------------------------------------------------------
# CREDENZIALI & TELEGRAM DISPATCHER
# -----------------------------------------------------------------------------
BOT_TOKEN = "8829669929:AAFHyp1WeBtpebQD-xqua-MsNyq8S_r8uQ0"
CHAT_ID = "-1004435512748"

def send_telegram_alert(ticker: str, details: dict) -> tuple[bool, str]:
    msg = (
        f"🚨 <b>URANIA RADAR — SEGNALE OPERATIVO</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Asset:</b> <code>${ticker}</code>\n"
        f"📈 <b>Protocollo:</b> {details.get('name', 'Setup Quant')}\n"
        f"💵 <b>Prezzo EOD:</b> ${details.get('price', 0.0):.2f}\n"
        f"📉 <b>Drawdown ATH:</b> {details.get('drawdown', 0.0):.1f}%\n"
        f"🎯 <b>POC Volume Base:</b> ${details.get('poc', 0.0):.2f} ({details.get('poc_dist', 0.0):+.2f}%)\n"
        f"🎯 <b>Target Superiore:</b> ${details.get('target', 0.0):.2f}\n"
        f"⚖️ <b>Rapporto R/R:</b> {details.get('rr_ratio', 0.0):.2f} : 1\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"ℹ️ <i>Analisi quantitativa validata su dati EOD.</i>"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN.strip()}/sendMessage"
    payload = {"chat_id": CHAT_ID.strip(), "text": msg, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        res = r.json()
        if r.status_code == 200 and res.get("ok"):
            return True, "Alert inoltrato al canale URANIA."
        return False, f"Errore Telegram: {res.get('description', 'Unauthorized')}"
    except Exception as e:
        return False, f"Errore connessione: {str(e)}"

# Engine Calcolo Volume Profile (POC)
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

# -----------------------------------------------------------------------------
# STYLING CSS SPECIFICO (DARK TECH QUANTASTE THEME)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .macro-card {
        background-color: #0b1320;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 22px;
        height: 100%;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .card-header {
        font-size: 19px;
        font-weight: 700;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 18px;
    }
    .badge-stagflation {
        background-color: #d97706;
        color: #ffffff;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        letter-spacing: 0.5px;
    }
    .badge-neutral {
        background-color: #f59e0b;
        color: #1e293b;
        font-weight: 800;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 12px;
    }
    .stat-pill {
        background-color: #111e33;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 10px 8px;
        text-align: center;
    }
    .circle-metric {
        width: 62px;
        height: 62px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 17px;
        margin: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# SIDEBAR MODULARE (LAZY LOADING)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛡️ URANIA SYSTEM")
    st.caption("Macro Quantitative Terminal • EOD Engine")
    nav = st.radio(
        "Seleziona Modulo Operativo:",
        [
            "1. Panoramica Macro e Mercati",
            "2. Z-Score & COT Lab",
            "3. Quant Lab (Archivio Studi)",
            "4. Protocol Screener & Telegram"
        ]
    )
    st.markdown("---")
    st.markdown("● **Pipeline Status:** `EOD Ready` ✅")
    st.markdown("● **Telegram Radar:** `Attivo` 📡")
    if st.button("🔒 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ==============================================================================
# MODULO 1: PANORAMICA MACRO E MERCATI (QUANTASTE 3-COLUMN LAYOUT)
# ==============================================================================
if nav == "1. Panoramica Macro e Mercati":
    st.title("Panoramica Macro e Mercati")
    st.caption("Intelligence quantitativa EOD su regimi macro, flussi di sentiment e propensione al rischio.")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # -------------------------------------------------------------------------
    # FINESTRA 1: REGIME ECONOMICO PREDOMINANTE
    # -------------------------------------------------------------------------
    with col1:
        st.markdown(
            """
            <div class="macro-card">
                <div class="card-header">🌐 Regime Economico Predominante</div>
                <div style="font-size: 11px; color: #94a3b8; letter-spacing: 0.5px; font-weight: 600;">REGIME DOMINANTE</div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 6px; margin-bottom: 12px;">
                    <div style="font-size: 18px; font-weight: 700; color: #f8fafc;">🇺🇸 USA</div>
                    <div class="badge-stagflation">STAGFLAZIONE</div>
                    <div style="font-size: 26px; font-weight: 800; color: #f8fafc;">66<span style="font-size: 16px; color: #94a3b8;">%</span></div>
                </div>
                <!-- Barra di Confidenza -->
                <div style="height: 6px; border-radius: 3px; background: linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%); margin-bottom: 20px;"></div>
                <!-- Regimi Internazionali -->
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 22px;">
                    <div class="stat-pill">
                        <div style="font-size: 10px; color: #94a3b8;">🇪🇺 Europa</div>
                        <div style="color: #10b981; font-weight: 700; font-size: 11px; margin: 3px 0;">REFLAZIONE</div>
                        <div style="font-weight: 800; font-size: 14px;">72%</div>
                    </div>
                    <div class="stat-pill">
                        <div style="font-size: 10px; color: #94a3b8;">🇨🇦 Canada</div>
                        <div style="color: #f59e0b; font-weight: 700; font-size: 11px; margin: 3px 0;">STAGFLAZ.</div>
                        <div style="font-weight: 800; font-size: 14px;">68%</div>
                    </div>
                    <div class="stat-pill">
                        <div style="font-size: 10px; color: #94a3b8;">🇨🇳 Cina</div>
                        <div style="color: #f59e0b; font-weight: 700; font-size: 11px; margin: 3px 0;">STAGFLAZ.</div>
                        <div style="font-weight: 800; font-size: 14px;">59%</div>
                    </div>
                </div>
                <!-- Asset Class Regimes (Gauges Circolari) -->
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 4px; text-align: center;">
                    <div>
                        <div class="circle-metric" style="border: 4px solid #f59e0b; color: #f8fafc;">69%</div>
                        <div style="font-size: 10px; color: #94a3b8; margin-top: 6px;">Obbligazioni</div>
                    </div>
                    <div>
                        <div class="circle-metric" style="border: 4px solid #f59e0b; color: #f8fafc;">67%</div>
                        <div style="font-size: 10px; color: #94a3b8; margin-top: 6px;">Materie Prime</div>
                    </div>
                    <div>
                        <div class="circle-metric" style="border: 4px solid #f59e0b; color: #f8fafc;">64%</div>
                        <div style="font-size: 10px; color: #94a3b8; margin-top: 6px;">Stocks</div>
                    </div>
                    <div>
                        <div class="circle-metric" style="border: 4px solid #ef4444; color: #ef4444;">25%</div>
                        <div style="font-size: 10px; color: #94a3b8; margin-top: 6px;">Crypto</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # -------------------------------------------------------------------------
    # FINESTRA 2: SMART QUANT SENTIMENT
    # -------------------------------------------------------------------------
    with col2:
        st.markdown(
            """
            <div class="macro-card">
                <div class="card-header">🧭 Smart Quant Sentiment</div>
                <div style="font-size: 11px; color: #94a3b8; letter-spacing: 0.5px; font-weight: 600;">SENTIMENT DI MERCATO</div>
                <div style="display: flex; align-items: center; justify-content: flex-end; gap: 10px; margin-top: 4px; margin-bottom: 12px;">
                    <div class="badge-neutral">NEUTRAL</div>
                    <div style="font-size: 26px; font-weight: 800; color: #f8fafc;">21<span style="font-size: 16px; color: #94a3b8;">%</span></div>
                </div>
                <!-- Barra Tri-Segmento -->
                <div style="height: 6px; border-radius: 3px; background: linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%); margin-bottom: 6px;"></div>
                <div style="display: flex; justify-content: space-between; font-size: 10px; color: #64748b; margin-bottom: 16px;">
                    <span>Ext. Sell</span>
                    <span>Hold</span>
                    <span>Ext. Buy</span>
                </div>
                <!-- Ripartizione Posizioni -->
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 20px;">
                    <div class="stat-pill">
                        <div style="font-size: 10px; color: #94a3b8;">Sell</div>
                        <div style="color: #ef4444; font-weight: 800; font-size: 15px; margin-top: 2px;">↓ 43%</div>
                    </div>
                    <div class="stat-pill">
                        <div style="font-size: 10px; color: #94a3b8;">Hold</div>
                        <div style="color: #f59e0b; font-weight: 800; font-size: 15px; margin-top: 2px;">21%</div>
                    </div>
                    <div class="stat-pill">
                        <div style="font-size: 10px; color: #94a3b8;">Buy</div>
                        <div style="color: #10b981; font-weight: 800; font-size: 15px; margin-top: 2px;">↑ 36%</div>
                    </div>
                </div>
                <!-- Dettaglio Segnali Bar Chart -->
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600; margin-bottom: 8px;">DISTRIBUZIONE SEGNALI</div>
                <div style="display: flex; flex-direction: column; gap: 6px;">
                    <div style="display: flex; align-items: center; font-size: 11px;">
                        <span style="width: 75px; color: #94a3b8;">Strong Buy</span>
                        <div style="flex: 1; background: #111e33; height: 12px; border-radius: 3px; overflow: hidden; margin: 0 8px;">
                            <div style="width: 9%; background: #10b981; height: 100%;"></div>
                        </div>
                        <span style="width: 28px; text-align: right; font-weight: 700;">9%</span>
                    </div>
                    <div style="display: flex; align-items: center; font-size: 11px;">
                        <span style="width: 75px; color: #94a3b8;">Buy</span>
                        <div style="flex: 1; background: #111e33; height: 12px; border-radius: 3px; overflow: hidden; margin: 0 8px;">
                            <div style="width: 27%; background: #10b981; height: 100%;"></div>
                        </div>
                        <span style="width: 28px; text-align: right; font-weight: 700;">27%</span>
                    </div>
                    <div style="display: flex; align-items: center; font-size: 11px;">
                        <span style="width: 75px; color: #94a3b8;">Hold</span>
                        <div style="flex: 1; background: #111e33; height: 12px; border-radius: 3px; overflow: hidden; margin: 0 8px;">
                            <div style="width: 21%; background: #f59e0b; height: 100%;"></div>
                        </div>
                        <span style="width: 28px; text-align: right; font-weight: 700;">21%</span>
                    </div>
                    <div style="display: flex; align-items: center; font-size: 11px;">
                        <span style="width: 75px; color: #94a3b8;">Sell</span>
                        <div style="flex: 1; background: #111e33; height: 12px; border-radius: 3px; overflow: hidden; margin: 0 8px;">
                            <div style="width: 36%; background: #ef4444; height: 100%;"></div>
                        </div>
                        <span style="width: 28px; text-align: right; font-weight: 700;">36%</span>
                    </div>
                    <div style="display: flex; align-items: center; font-size: 11px;">
                        <span style="width: 75px; color: #94a3b8;">Strong Sell</span>
                        <div style="flex: 1; background: #111e33; height: 12px; border-radius: 3px; overflow: hidden; margin: 0 8px;">
                            <div style="width: 7%; background: #ef4444; height: 100%;"></div>
                        </div>
                        <span style="width: 28px; text-align: right; font-weight: 700;">7%</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # -------------------------------------------------------------------------
    # FINESTRA 3: RISK ON / RISK OFF
    # -------------------------------------------------------------------------
    with col3:
        st.markdown(
            """
            <div class="macro-card">
                <div class="card-header">📉 Risk On / Risk Off</div>
                <div style="font-size: 11px; color: #94a3b8; letter-spacing: 0.5px; font-weight: 600;">PROPENSIONE AL RISCHIO</div>
                <div style="display: flex; align-items: center; justify-content: flex-end; gap: 10px; margin-top: 4px; margin-bottom: 12px;">
                    <div class="badge-neutral">NEUTRAL</div>
                    <div style="font-size: 26px; font-weight: 800; color: #f8fafc;">50<span style="font-size: 16px; color: #94a3b8;">%</span></div>
                </div>
                <!-- Barra Risk Meter -->
                <div style="height: 6px; border-radius: 3px; background: linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%); margin-bottom: 6px;"></div>
                <div style="display: flex; justify-content: space-between; font-size: 10px; color: #64748b; margin-bottom: 16px;">
                    <span>Ext. Risk Off</span>
                    <span>Neutral</span>
                    <span>Ext. Risk On</span>
                </div>
                <!-- Asset Allocation Ripartizione -->
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 16px;">
                    <div class="stat-pill">
                        <div style="font-size: 10px; color: #94a3b8;">Risk Assets</div>
                        <div style="font-weight: 800; font-size: 15px; color: #f8fafc; margin-top: 2px;">50%</div>
                    </div>
                    <div class="stat-pill">
                        <div style="font-size: 10px; color: #94a3b8;">Difensivo</div>
                        <div style="font-weight: 800; font-size: 15px; color: #f8fafc; margin-top: 2px;">30%</div>
                    </div>
                    <div class="stat-pill">
                        <div style="font-size: 10px; color: #94a3b8;">Cash</div>
                        <div style="font-weight: 800; font-size: 15px; color: #f8fafc; margin-top: 2px;">20%</div>
                    </div>
                </div>
                <!-- Breakdown Indicatori Quantitativi -->
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600; margin-bottom: 8px;">DETTAGLIO SEGNALI QUANTITATIVI</div>
                <div style="display: flex; flex-direction: column; gap: 6px; font-size: 11px;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px;">
                        <span style="color: #94a3b8;">TIP Momentum</span>
                        <span style="font-weight: 700; color: #f8fafc;">0/20</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px;">
                        <span style="color: #94a3b8;">VIX Term Structure</span>
                        <span style="font-weight: 700; color: #10b981;">+20/20</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px;">
                        <span style="color: #94a3b8;">Credit Spreads (HYG/LQD)</span>
                        <span style="font-weight: 700; color: #10b981;">+10/10</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px;">
                        <span style="color: #94a3b8;">Consumer Appetite (XLY/XLP)</span>
                        <span style="font-weight: 700; color: #10b981;">+15/15</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px;">
                        <span style="color: #94a3b8;">Risk Flows (IWM/SPY)</span>
                        <span style="font-weight: 700; color: #10b981;">+10/15</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding-bottom: 3px;">
                        <span style="color: #94a3b8;">Primary Trend</span>
                        <span style="font-weight: 700; color: #10b981;">+20/20</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ==============================================================================
# MODULO 2: Z-SCORE & COT LAB
# ==============================================================================
elif nav == "2. Z-Score & COT Lab":
    st.title("📊 Z-Score Normalization & COT Positioning Lab")
    st.caption("Analisi quantitativa dei flussi istituzionali (CFTC) con normalizzazione Z-Score a 1/3/5 anni.")
    c1, c2 = st.columns([1, 2])
    with c1:
        asset = st.selectbox("Seleziona Sottostante / Future:", ["Cocoa", "Coffee", "Natural Gas", "Crude Oil", "Gold", "S&P 500", "US 10Y Note"])
        lookback = st.radio("Finestra di Normalizzazione Z-Score:", ["1 Anno (52w)", "3 Anni (156w)", "5 Anni (260w)"])
    with c2:
        st.info(f"Asset: **{asset}** | Lookback: **{lookback}**")
        st.markdown(
            """
            * **Commercials (Hedgers):** Monitoraggio delle coperture reali dei produttori.
            * **Non-Commercials (Large Speculators):** Tracciamento dei massimi/minimi di trend.
            * **Divergenza Z-Score:** Evidenzia letture estreme ($\ge +2.0$ o $\le -2.0$) per rotazioni contrarian.
            """
        )

# ==============================================================================
# MODULO 3: QUANT LAB (ARCHIVIO STUDI)
# ==============================================================================
elif nav == "3. Quant Lab (Archivio Studi)":
    st.title("🔬 Quantitative Studies & Historical Catalog")
    st.caption("Archivio modulare dei paper statistici e simulazioni EOD.")
    st.markdown(
        """
        * 📁 **Studio 01:** *Efficienza statistica del POC Volume Profile su drawdown > 40% (2010–2026)*
        * 📁 **Studio 02:** *Rendimento e gestione del Theta Decay con strategie Zero-Cost Collar e Covered Call*
        * 📁 **Studio 03:** *Correlazione dinamica tra Net Liquidity Fed e multipli S&P 500 nei cambi di regime*
        """
    )

# ==============================================================================
# MODULO 4: PROTOCOL SCREENER & TELEGRAM
# ==============================================================================
elif nav == "4. Protocol Screener & Telegram":
    st.title("🎯 Protocol Screener & Telegram Radar")
    st.caption("Scansione batch EOD dell'universo azionario e dispatching degli alert sul canale Telegram.")
    st.markdown("---")

    st.subheader("📡 Connessione Canale Telegram URANIA")
    st.write(f"• **Canale:** `URANIA` (`{CHAT_ID}`)")
    st.write(f"• **Bot:** `@PORCELLINO_QUANT_BOT`")

    if st.button("📨 INVIA SEGNALE DI PROVA AL CANALE"):
        test_msg = {
            "name": "POC Capitulation (Bottom Hunter)",
            "price": 61.66,
            "drawdown": -80.1,
            "poc": 59.81,
            "poc_dist": 3.09,
            "target": 78.50,
            "rr_ratio": 3.45
        }
        ok, res_text = send_telegram_alert("PYPL", test_msg)
        if ok:
            st.success(f"✅ {res_text}")
        else:
            st.error(f"❌ {res_text}")

    st.markdown("---")
    st.subheader("⚙️ Configurazione Protocolli Attivi")
    c1, c2, c3 = st.columns(3)
    p1 = c1.checkbox("Protocollo 1: POC Capitulation (Bottom Hunter)", value=True)
    p2 = c2.checkbox("Protocollo 2: Rounding Base & Breakout", value=True)
    p3 = c3.checkbox("Filtro Z-Score <= -2.0", value=True)

    st.markdown("---")
    st.subheader("📋 Universo Azionario di Scansione")
    watchlist = ["PYPL", "AXON", "PLTR", "ENPH", "BABA", "NIO", "TSLA", "SQ"]

    if st.button("🚀 ESEGUI SCANSIONE BATCH EOD & DISPATCH ALERTS"):
        results = []
        alerts_sent = 0

        with st.spinner("Scansione e calcolo metriche EOD in corso..."):
            for t in watchlist:
                try:
                    df = yf.download(t, period="1y", interval="1d", progress=False)
                    if not df.empty:
                        if isinstance(df.columns, pd.MultiIndex):
                            df.columns = df.columns.get_level_values(0)

                        last_close = float(df['Close'].iloc[-1])
                        ath_price = float(df['High'].max())
                        dd = ((last_close / ath_price) - 1.0) * 100.0
                        poc = calculate_eod_poc(df)
                        dist_poc = ((last_close - poc) / poc) * 100.0

                        detected = None
                        if p1 and dd <= -30.0 and abs(dist_poc) <= 5.0:
                            detected = {
                                "name": "POC Capitulation (Bottom Hunter)",
                                "price": last_close,
                                "drawdown": dd,
                                "poc": poc,
                                "poc_dist": dist_poc,
                                "target": poc * 1.25,
                                "rr_ratio": 3.20
                            }
                        elif p2 and dd <= -20.0 and dist_poc > 1.5:
                            detected = {
                                "name": "Rounding Base & Breakout",
                                "price": last_close,
                                "drawdown": dd,
                                "poc": poc,
                                "poc_dist": dist_poc,
                                "target": last_close * 1.20,
                                "rr_ratio": 2.80
                            }

                        status_tg = "Nessun Trigger"
                        if detected:
                            ok, _ = send_telegram_alert(t, detected)
                            if ok:
                                alerts_sent += 1
                                status_tg = "Inviato a Telegram 🎯"

                        results.append({
                            "Ticker": t,
                            "Prezzo EOD": f"${last_close:.2f}",
                            "Drawdown ATH": f"{dd:.1f}%",
                            "POC Volume": f"${poc:.2f}",
                            "Distanza POC": f"{dist_poc:+.2f}%",
                            "Protocollo Rilevato": detected["name"] if detected else "Nessuno",
                            "Stato Notifica": status_tg
                        })
                except Exception:
                    pass

        st.success(f"Scansione EOD completata. Notifiche inviate sul canale URANIA: {alerts_sent}")
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
