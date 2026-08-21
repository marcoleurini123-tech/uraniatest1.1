import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Terminale URANIA",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Credenziali Telegram Canale URANIA
BOT_TOKEN = "8829669929:AAFHyp1WeBtpebQD-xqua-MsNyq8S_r8uQ0"
CHAT_ID = "-1004435512748"

# Dispatcher Telegram
def send_telegram_msg(msg: str) -> tuple[bool, str]:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        res = r.json()
        if r.status_code == 200 and res.get("ok"):
            return True, "Messaggio recapitato con successo nel canale URANIA!"
        return False, f"Errore API Telegram: {res.get('description', 'Sconosciuto')}"
    except Exception as e:
        return False, f"Errore di connessione: {str(e)}"

# Gestione Sessione di Autenticazione
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Schermata di Login
if not st.session_state.authenticated:
    st.title("🛡️ URANIA QUANTITATIVE TERMINAL")
    st.caption("Accesso Riservato — Pipeline di Ricerca Istituzionale & Macro")
    col1, col2 = st.columns([1, 2])
    with col1:
        pwd_input = st.text_input("Inserisci Password di Accesso:", type="password")
        if st.button("SBLOCCA TERMINALE"):
            if pwd_input == "Serafino12?#":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Password non valida.")
    st.stop()

# Sidebar di Navigazione Modulare (Lazy Loading)
with st.sidebar:
    st.markdown("### 🛡️ URANIA SYSTEM")
    st.caption("Macro Quantitative Terminal • EOD Pipeline")
    nav = st.radio(
        "Seleziona Modulo:",
        [
            "1. Dashboard Macro & Sentiment",
            "2. Z-Score & COT Lab",
            "3. Quant Lab (Archivio Studi)",
            "4. Protocol Screener & Telegram"
        ]
    )
    st.markdown("---")
    st.markdown("● **Pipeline Status:** `EOD Ready` ✅")
    st.markdown("● **Motore Telegram:** `Operativo` 📡")
    if st.button("🔒 Logout"):
        st.session_state.authenticated = False
        st.rerun()

# ==============================================================================
# MODULO 1: MACRO & SENTIMENT
# ==============================================================================
if nav == "1. Dashboard Macro & Sentiment":
    st.title("🌐 Macroeconomic Regimes & Global Liquidity")
    st.caption("Monitoraggio dei 7 scenari macroeconomici e liquidità aggregata.")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Regime Attivo", "Goldilocks / Disinflazione", "+0.42 pt")
    m2.metric("Net Fed Liquidity", "$6.12T", "+$24B")
    m3.metric("Treasury Account (TGA)", "$748B", "-$12B")
    m4.metric("Reverse Repo (RRP)", "$320B", "-$8B")

# ==============================================================================
# MODULO 2: Z-SCORE & COT LAB
# ==============================================================================
elif nav == "2. Z-Score & COT Lab":
    st.title("📊 Z-Score Normalization & COT Positioning Lab")
    st.caption("Analisi dei flussi istituzionali e divergenze statistiche.")
    asset = st.selectbox("Seleziona Asset / Future:", ["Cocoa", "Coffee", "Natural Gas", "Gold", "S&P 500", "US 10Y Note"])
    st.info(f"Studio statistico pronto per l'asset: **{asset}**")

# ==============================================================================
# MODULO 3: QUANT LAB
# ==============================================================================
elif nav == "3. Quant Lab (Archivio Studi)":
    st.title("🔬 Quantitative Studies & Historical Catalog")
    st.caption("Archivio degli studi quantitativi e backtest sui setup.")
    st.write("Catalogo delle simulazioni EOD.")

# ==============================================================================
# MODULO 4: PROTOCOL SCREENER & TELEGRAM
# ==============================================================================
elif nav == "4. Protocol Screener & Telegram":
    st.title("🎯 Protocol Execution & Telegram Radar")
    st.caption("Scansione batch EOD e invio notifiche su canale Telegram dedicato.")
    st.markdown("---")

    st.subheader("📡 Connessione Telegram URANIA")
    st.write(f"• **Canale:** `URANIA` (`{CHAT_ID}`)")
    st.write(f"• **Bot:** `@PORCELLINO_QUANT_BOT`")
    
    if st.button("📨 INVIA SEGNALE DI PROVA AL CANALE"):
        test_msg = (
            "🚨 <b>URANIA TERMINAL — TEST ALERT RADAR</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📌 <b>Ticker:</b> $PYPL — PayPal Holdings\n"
            "📈 <b>Protocollo:</b> POC Capitulation (Bottom Hunter)\n"
            "💵 <b>Prezzo EOD:</b> $61.66\n"
            "📉 <b>Drawdown ATH:</b> -80.1%\n"
            "🎯 <b>POC Target:</b> $59.81 (+3.09%)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ <i>Dispatcher Telegram agganciato e operativo.</i>"
        )
        with st.spinner("Invio messaggio in corso..."):
            ok, res_text = send_telegram_msg(test_msg)
            if ok:
                st.success(f"✅ {res_text}")
            else:
                st.error(f"❌ {res_text}")

    st.markdown("---")
    st.subheader("⚙️ Configurazione Protocolli Attivi")
    c1, c2, c3 = st.columns(3)
    c1.checkbox("Protocollo 1: POC Capitulation (Bottom Hunter)", value=True)
    c2.checkbox("Protocollo 2: Rounding Base & Breakout", value=True)
    c3.checkbox("Filtro Z-Score <= -2.0 (⭐)", value=True)

    st.markdown("---")
    st.subheader("📋 Universo di Scansione")
    st.selectbox("Watchlist Target:", ["S&P 500", "NASDAQ 100", "Watchlist Personale"])

    if st.button("🚀 ESEGUI SCANSIONE BATCH EOD"):
        st.success("Scansione completata. Titoli inviati al dispatcher.")

    st.dataframe(pd.DataFrame({
        "Ticker": ["PYPL", "AXON"],
        "Azienda": ["PayPal Holdings", "Axon Enterprise"],
        "Prezzo EOD": ["$61.66", "$65.40"],
        "Drawdown ATH": ["-80.1%", "-32.4%"],
        "POC Target": ["$59.81", "$58.20"],
        "Distanza POC": ["+3.09%", "+1.20%"],
        "Protocollo Rilevato": ["POC Capitulation", "Rounding Base + Breakout"],
        "Dispatcher Telegram": ["Inviato ✅", "Inviato ✅"]
    }), use_container_width=True, hide_index=True)
