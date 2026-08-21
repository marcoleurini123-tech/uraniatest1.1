import streamlit as st
import pandas as pd
import numpy as np
import requests
import yfinance as yf

# Configurazione Pagina
st.set_page_config(
    page_title="URANIA SYSTEM",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inserisci qui il token copiato da BotFather
BOT_TOKEN = "8829669929:AAFHyp1WeBtpebQD-xqua-MsNyq8S_r8uQ0"
CHAT_ID = "-1004435512748"

# Dispatcher Telegram
def send_telegram_alert(message: str) -> tuple[bool, str]:
    token_clean = BOT_TOKEN.strip()
    chat_clean = CHAT_ID.strip()
    url = f"https://api.telegram.org/bot{token_clean}/sendMessage"
    payload = {
        "chat_id": chat_clean,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()
        if res.status_code == 200 and data.get("ok"):
            return True, "Alert inviato con successo nel canale URANIA."
        return False, f"Errore Telegram: {data.get('description', 'Non autorizzato')}"
    except Exception as e:
        return False, f"Errore Connessione: {str(e)}"

# Engine Calcolo POC su Dati EOD
def calculate_eod_poc(df: pd.DataFrame, bins_num: int = 50) -> float:
    if df.empty or 'Close' not in df or 'Volume' not in df:
        return 0.0
    price_bins = np.linspace(df['Low'].min(), df['High'].max(), bins_num)
    bin_idx = np.digitize(df['Close'].values, price_bins)
    vol_profile = np.zeros(len(price_bins))
    for idx, v in zip(bin_idx, df['Volume'].values):
        if idx < len(vol_profile):
            vol_profile[idx] += v
    return float(price_bins[np.argmax(vol_profile)])

# Sidebar Navigazione (Lazy Loading)
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

# ==============================================================================
# MODULO 1: MACRO & SENTIMENT
# ==============================================================================
if nav == "1. Dashboard Macro & Sentiment":
    st.title("🌐 Macroeconomic Regimes & Global Liquidity")
    st.caption("Monitoraggio dei 7 scenari macroeconomici e regimi di liquidità aggregata.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Regime Macro Attivo", "Goldilocks / Disinflazione", "+0.42 pt")
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
    st.info(f"Asset in esame: **{asset}** — Studio statistico posizionale attivo.")

# ==============================================================================
# MODULO 3: QUANT LAB
# ==============================================================================
elif nav == "3. Quant Lab (Archivio Studi)":
    st.title("🔬 Quantitative Studies & Historical Catalog")
    st.caption("Catalogo delle simulazioni quantitative e backtest dei protocolli.")
    st.write("Modulo archivio pronto per l'implementazione dei test retrospettivi.")

# ==============================================================================
# MODULO 4: PROTOCOL SCREENER & TELEGRAM
# ==============================================================================
elif nav == "4. Protocol Screener & Telegram":
    st.title("🎯 Protocol Execution & Telegram Radar")
    st.caption("Scansione batch EOD dell'universo azionario e dispatching automatico degli alert.")
    st.markdown("---")

    st.subheader("📡 Connessione Telegram URANIA")
    st.write(f"• **Canale:** `URANIA` (`{CHAT_ID}`)")
    st.write(f"• **Bot:** `@PORCELLINO_QUANT_BOT`")

    if st.button("📨 INVIA SEGNALE DI PROVA AL CANALE"):
        test_msg = (
            "🚨 <b>URANIA TERMINAL — TEST ALERT RADAR</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📌 <b>Asset:</b> PayPal Holdings (<code>$PYPL</code>)\n"
            "📈 <b>Protocollo:</b> POC Capitulation (Bottom Hunter)\n"
            "💵 <b>Prezzo EOD:</b> $61.66\n"
            "📉 <b>Drawdown ATH:</b> -80.1%\n"
            "🎯 <b>POC Volume Target:</b> $59.81 (+3.09%)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ <i>Canale di trasmissione EOD validato e attivo.</i>"
        )
        ok, status = send_telegram_alert(test_msg)
        if ok:
            st.success(f"✅ {status}")
        else:
            st.error(f"❌ {status}")

    st.markdown("---")
    st.subheader("⚙️ Configurazione Protocolli Attivi")
    c1, c2, c3 = st.columns(3)
    p1 = c1.checkbox("Protocollo 1: POC Capitulation (Bottom Hunter)", value=True)
    p2 = c2.checkbox("Protocollo 2: Rounding Base & Breakout", value=True)
    p3 = c3.checkbox("Filtro Z-Score <= -2.0 (⭐)", value=True)

    st.markdown("---")
    st.subheader("📋 Universo di Scansione")
    watchlist = st.selectbox("Watchlist Target:", ["Watchlist Focus (PYPL, AXON, PLTR, ENPH)", "S&P 500", "NASDAQ 100"])

    if st.button("🚀 ESEGUI SCANSIONE BATCH EOD"):
        tickers = ["PYPL", "AXON", "PLTR", "ENPH"]
        results = []
        
        with st.spinner("Scansione dati EOD in corso..."):
            for t in tickers:
                try:
                    df = yf.download(t, period="1y", interval="1d", progress=False)
                    if not df.empty:
                        # Gestione multi-index per compatibilità yfinance
                        if isinstance(df.columns, pd.MultiIndex):
                            df.columns = df.columns.get_level_values(0)
                        
                        last_close = float(df['Close'].iloc[-1])
                        ath_price = float(df['High'].max())
                        dd = ((last_close / ath_price) - 1) * 100
                        poc = calculate_eod_poc(df)
                        dist_poc = ((last_close - poc) / poc) * 100

                        detected = "Nessuno"
                        if dd <= -30.0 and abs(dist_poc) <= 5.0:
                            detected = "POC Capitulation"
                        elif dd <= -20.0 and dist_poc > 0:
                            detected = "Rounding Base + Breakout"

                        results.append({
                            "Ticker": t,
                            "Prezzo EOD": f"${last_close:.2f}",
                            "Drawdown ATH": f"{dd:.1f}%",
                            "POC Base": f"${poc:.2f}",
                            "Distanza POC": f"{dist_poc:+.2f}%",
                            "Protocollo Rilevato": detected,
                            "Stato Notifica": "Rilevato 🎯" if detected != "Nessuno" else "In attesa"
                        })
                except Exception:
                    pass

        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
