
import streamlit as st
import pandas as pd
import requests

from core.data_engine import fetch_eod_data, calculate_eod_poc
from protocols.poc_capitulation import evaluate_poc_capitulation
from protocols.rounding_breakout import evaluate_rounding_breakout

st.set_page_config(
    page_title="URANIA SYSTEM",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Parametri Canale Telegram URANIA
BOT_TOKEN = "8829669929:AAFHyp1WeBtpebQD-xqua-MsNyq8S_r8uQ0"
CHAT_ID = "-1004435512748"

def send_telegram_alert(ticker: str, details: dict) -> tuple[bool, str]:
    msg = (
        f"🚨 <b>URANIA RADAR — SEGNALE OPERATIVO</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Asset:</b> <code>${ticker}</code>\n"
        f"📈 <b>Protocollo:</b> {details['name']}\n"
        f"💵 <b>Prezzo EOD:</b> ${details['price']:.2f}\n"
        f"📉 <b>Drawdown ATH:</b> {details['drawdown']:.1f}%\n"
        f"🎯 <b>POC Base:</b> ${details['poc']:.2f} ({details['poc_dist']:+.2f}%)\n"
        f"🎯 <b>Target POC Superiore:</b> ${details['target']:.2f}\n"
        f"⚖️ <b>Rapporto R/R:</b> {details['rr_ratio']:.2f} : 1\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <i>Analisi quantitativa validata su dati EOD.</i>"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN.strip()}/sendMessage"
    payload = {"chat_id": CHAT_ID.strip(), "text": msg, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        res = r.json()
        if r.status_code == 200 and res.get("ok"):
            return True, "Alert inviato al canale URANIA."
        return False, f"Errore API Telegram: {res.get('description', 'Unauthorized')}"
    except Exception as e:
        return False, f"Errore di connessione: {str(e)}"

# Autenticazione Accesso
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ URANIA QUANTITATIVE TERMINAL")
    st.caption("Pipeline Istituzionale di Ricerca Macro & Screening EOD")
    col1, _ = st.columns([1, 2])
    with col1:
        pwd = st.text_input("Password di Accesso:", type="password")
        if st.button("SBLOCCA TERMINALE"):
            if pwd == "Serafino12?#":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Credenziali non corrette.")
    st.stop()

# Sidebar di Navigazione
with st.sidebar:
    st.markdown("### 🛡️ URANIA SYSTEM")
    st.caption("Macro Quantitative Terminal • EOD Engine")
    nav = st.radio(
        "Seleziona Modulo Operativo:",
        [
            "1. Dashboard Macro & Sentiment",
            "2. Z-Score & COT Lab",
            "3. Quant Lab (Archivio Studi)",
            "4. Protocol Screener & Telegram"
        ]
    )
    st.markdown("---")
    st.markdown("● **Pipeline Status:** `EOD Ready` ✅")
    st.markdown("● **Telegram Radar:** `Attivo` 📡")
    if st.button("🔒 Logout"):
        st.session_state.auth = False
        st.rerun()

# ==============================================================================
# MODULO 1: MACRO & SENTIMENT
# ==============================================================================
if nav == "1. Dashboard Macro & Sentiment":
    st.title("🌐 Macroeconomic Regimes & Global Liquidity")
    st.caption("Monitoraggio dei 7 scenari macroeconomici e liquidità aggregata.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Regime Attivo", "Goldilocks / Disinflazione", "+0.42 pt")
    c2.metric("Net Fed Liquidity", "$6.12T", "+$24B w/w")
    c3.metric("US Treasury (TGA)", "$748B", "-$12B")
    c4.metric("Reverse Repo (RRP)", "$320B", "-$8B")

# ==============================================================================
# MODULO 2: Z-SCORE & COT LAB
# ==============================================================================
elif nav == "2. Z-Score & COT Lab":
    st.title("📊 Z-Score Normalization & COT Positioning Lab")
    st.caption("Analisi dei flussi istituzionali e divergenze statistiche a 1/3/5 anni.")
    asset = st.selectbox("Seleziona Sottostante:", ["Cocoa", "Coffee", "Natural Gas", "Gold", "S&P 500", "US 10Y Note"])
    st.info(f"Asset selezionato: **{asset}** — Modulo statistico posizionale caricato.")

# ==============================================================================
# MODULO 3: QUANT LAB
# ==============================================================================
elif nav == "3. Quant Lab (Archivio Studi)":
    st.title("🔬 Quantitative Studies & Historical Catalog")
    st.caption("Archivio storico delle simulazioni e backtest proprietari.")
    st.write("Catalogo delle simulazioni quantitative EOD.")

# ==============================================================================
# MODULO 4: PROTOCOL SCREENER & TELEGRAM
# ==============================================================================
elif nav == "4. Protocol Screener & Telegram":
    st.title("🎯 Protocol Screener & Telegram Radar")
    st.caption("Scansione quantitativa EOD dell'universo azionario e dispatching degli alert.")
    st.markdown("---")

    st.subheader("⚙️ Configurazione Protocolli Attivi")
    c1, c2, c3 = st.columns(3)
    p1 = c1.checkbox("Protocollo 1: POC Capitulation (Bottom Hunter)", value=True)
    p2 = c2.checkbox("Protocollo 2: Rounding Base & Breakout", value=True)
    p3 = c3.checkbox("Filtro Z-Score <= -2.0", value=True)

    st.markdown("---")
    st.subheader("📋 Universo Azionario di Scansione")
    
    # Watchlist di monitoraggio
    watchlist = ["PYPL", "AXON", "PLTR", "ENPH", "BABA", "NIO", "TSLA", "SQ", "SHOP"]
    
    if st.button("🚀 ESEGUI SCANSIONE BATCH EOD & DISPATCH ALERTS"):
        results = []
        alerts_sent = 0

        with st.spinner("Scansione e calcolo metriche EOD in corso..."):
            for t in watchlist:
                df = fetch_eod_data(t, period="1y")
                if not df.empty:
                    last_close = float(df['Close'].iloc[-1])
                    ath_price = float(df['High'].max())
                    dd = ((last_close / ath_price) - 1.0) * 100.0
                    poc = calculate_eod_poc(df)
                    dist_poc = ((last_close - poc) / poc) * 100.0

                    detected_protocol = None
                    if p1:
                        detected_protocol = evaluate_poc_capitulation(df)
                    if not detected_protocol and p2:
                        detected_protocol = evaluate_rounding_breakout(df)

                    status_tg = "Nessun Trigger"
                    if detected_protocol:
                        ok, _ = send_telegram_alert(t, detected_protocol)
                        if ok:
                            alerts_sent += 1
                            status_tg = "Inviato a Telegram 🎯"

                    results.append({
                        "Ticker": t,
                        "Prezzo EOD": f"${last_close:.2f}",
                        "Drawdown ATH": f"{dd:.1f}%",
                        "POC Base": f"${poc:.2f}",
                        "Distanza POC": f"{dist_poc:+.2f}%",
                        "Protocollo Rilevato": detected_protocol["name"] if detected_protocol else "Nessuno",
                        "Stato Telegram": status_tg
                    })

        st.success(f"Scansione EOD completata. Notifiche inviate sul canale URANIA: {alerts_sent}")
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
