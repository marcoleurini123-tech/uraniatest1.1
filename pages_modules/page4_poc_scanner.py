import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests

BOT_TOKEN = "8829669929:AAFHyp1WeBtpebQD-xqua-MsNyq8S_r8uQ0"
CHAT_ID = "-1004435512748"

def send_tg_alert(ticker: str, details: dict):
    msg = (
        f"🚨 <b>URANIA RADAR — SEGNALE POC SCANNER</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Asset:</b> <code>${ticker}</code>\n"
        f"📈 <b>Protocollo:</b> {details.get('protocol')}\n"
        f"💵 <b>Prezzo EOD:</b> ${details.get('price', 0.0):.2f}\n"
        f"📉 <b>Drawdown ATH:</b> {details.get('drawdown', 0.0):.1f}%\n"
        f"🎯 <b>POC Volume:</b> ${details.get('poc', 0.0):.2f} ({details.get('poc_dist', 0.0):+.2f}%)\n"
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
        return r.status_code == 200 and r.json().get("ok")
    except Exception:
        return False

def calc_poc(df: pd.DataFrame, bins: int = 50) -> float:
    if df.empty or 'Close' not in df or 'Volume' not in df: return 0.0
    pb = np.linspace(df['Low'].min(), df['High'].max(), bins)
    b_idx = np.digitize(df['Close'].values, pb)
    vh = np.zeros(len(pb))
    for idx, v in zip(b_idx, df['Volume'].values):
        if idx < len(vh): vh[idx] += v
    return float(pb[np.argmax(vh)])

def render_page4():
    st.title("🎯 POC Scanner & Telegram Radar (Setup Massimo Rea)")
    st.caption("Scansione quantitativa EOD dell'universo azionario e dispatching automatico su canale Telegram.")
    st.markdown("---")

    st.write(f"• **Canale Telegram:** `URANIA` (`{CHAT_ID}`) | **Bot:** `@PORCELLINO_QUANT_BOT`")
    raw_list = st.text_area("Watchlist Titoli (separati da virgola):", "PYPL, AXON, PLTR, ENPH, BABA, NIO, TSLA, SQ, SHOP, AMD, NVDA, COIN, INTC, RIVN")
    tickers = [t.strip().upper() for t in raw_list.split(",") if t.strip()]

    c1, c2, c3 = st.columns(3)
    dd_lim = c1.slider("Min Drawdown ATH (%):", -85.0, -15.0, -30.0)
    poc_t = c2.slider("Tolleranza POC (%):", 1.0, 10.0, 5.0)
    z_flt = c3.checkbox("Filtro Z-Score <= -1.0", value=True)

    if st.button("🚀 ESEGUI SCANSIONE EOD & DISPATCH TELEGRAM"):
        res = []
        sent_c = 0
        with st.spinner("Scansione Volume Profile in corso..."):
            for t in tickers:
                try:
                    df_t = yf.download(t, period="1y", interval="1d", progress=False)
                    if not df_t.empty and len(df_t) >= 50:
                        if isinstance(df_t.columns, pd.MultiIndex): df_t.columns = df_t.columns.get_level_values(0)
                        last_c = float(df_t['Close'].iloc[-1])
                        ath = float(df_t['High'].max())
                        dd = ((last_c - ath) / ath) * 100.0
                        poc = calc_poc(df_t)
                        d_poc = ((last_c - poc) / poc) * 100.0
                        ret = df_t['Close'].pct_change()
                        z = float((ret.iloc[-1] - ret.mean()) / (ret.std() + 1e-9))

                        hit = None
                        if dd <= dd_lim and abs(d_poc) <= poc_t:
                            if not z_flt or z <= -1.0: hit = "POC Capitulation (Bottom Hunter)"
                        elif dd <= -20.0 and d_poc > 1.5: hit = "Rounding Base Breakout"

                        st_tg = "Nessun Trigger"
                        if hit:
                            target = poc * 1.25 if "Capitulation" in hit else last_c * 1.20
                            stop = poc * 0.95
                            rr = max(0.01, target - last_c) / max(0.01, last_c - stop)
                            if send_tg_alert(t, {"protocol": hit, "price": last_c, "drawdown": dd, "poc": poc, "poc_dist": d_poc, "z_score": z, "target": target, "rr_ratio": rr}):
                                sent_c += 1
                                st_tg = "Inviato a Telegram 🎯"

                        res.append({"Ticker": t, "Prezzo EOD": f"${last_c:.2f}", "Drawdown ATH": f"{dd:.1f}%", "POC Volume": f"${poc:.2f}", "Distanza POC": f"{d_poc:+.2f}%", "Z-Score": f"{z:.2f}", "Protocollo": hit if hit else "—", "Stato Telegram": st_tg})
                except Exception: pass
        st.success(f"Scansione completata. Segnali inviati a Telegram: {sent_c}")
        st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)
