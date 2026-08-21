import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import hmac

# --- 1. CONFIGURAZIONE LAYOUT ---
st.set_page_config(
    page_title="URANIA Terminal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. GATEWAY DI ACCESSO PRIVATO ---
ACCESS_PASSWORD = "Serafino12?#"

def check_password():
    def password_entered():
        if hmac.compare_digest(st.session_state["password_input"], ACCESS_PASSWORD):
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # Schermata Login Centrata
    col_l, col_c, col_r = st.columns([1, 1.8, 1])
    with col_c:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🛡️ URANIA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #A0AEC0; font-size: 14px;'>PRECISION. CONSISTENCY. GROWTH.</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.text_input("Chiave di Accesso:", type="password", on_change=password_entered, key="password_input")
        
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("⛔ Password non corretta. Accesso negato.")
            
        st.caption("Accesso riservato. Sessione autenticata con protocollo di sicurezza.")
    return False

if not check_password():
    st.stop()

# --- 3. SIDEBAR & CONTROLLO MODULARE ---
st.sidebar.markdown("## 🛡️ **URANIA SYSTEM**")
st.sidebar.caption("Macro Quantitative Terminal • EOD Pipeline")

nav_selection = st.sidebar.radio(
    "Seleziona Modulo:",
    [
        "1. Dashboard Macro & Sentiment",
        "2. Z-Score & COT Lab",
        "3. Quant Lab (Archivio Studi)",
        "4. Protocol Screener & Telegram"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Pipeline Status:** `EOD Ready` ✅")
st.sidebar.markdown("**Motore Telegram:** `Standby (Asincrono)` 📡")

# ==============================================================================
# PAGINA 1: DASHBOARD MACRO & SENTIMENT (READ-ONLY)
# ==============================================================================
if nav_selection == "1. Dashboard Macro & Sentiment":
    st.title("🌐 Dashboard Macroeconomica & Sentiment")
    st.caption("Visualizzazione EOD dei regimi di mercato, ampiezza e indicatori proprietari.")
    st.markdown("---")
    
    # LIVELLO 1: I 3 PILASTRI TOP-DOWN
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("### Regime Dominante (7 Scenari)")
        st.warning("USA: STAGFLAZIONE (66%)")
        st.progress(66)
        sub_c1, sub_c2, sub_c3 = st.columns(3)
        sub_c1.metric("Bonds", "69%")
        sub_c2.metric("Commodities", "67%")
        sub_c3.metric("Stocks", "64%")
        
    with c2:
        st.markdown("### Smart Quant Sentiment")
        st.info("SENTIMENT: NEUTRAL (21%)")
        st.progress(21)
        sub_s1, sub_s2, sub_s3 = st.columns(3)
        sub_s1.metric("Sell", "43%", delta="-7%", delta_color="inverse")
        sub_s2.metric("Hold", "21%")
        sub_s3.metric("Buy", "36%", delta="+4%")

    with c3:
        st.markdown("### Risk On / Risk Off Engine")
        st.warning("PROPENSIONE: NEUTRAL (50%)")
        st.progress(50)
        sub_r1, sub_r2, sub_r3 = st.columns(3)
        sub_r1.metric("Risk Assets", "50%")
        sub_r2.metric("Difensivo", "30%")
        sub_r3.metric("Cash", "20%")

    st.markdown("---")
    
    # LIVELLO 2: GRIGLIA KPI SEMAFORI
    st.subheader("🚦 Monitor Indicatori di Liquidità & Stress")
    kpi_row1 = st.columns(6)
    kpi_row1[0].metric("DIX", "46.2%", "🟢 BULLISH")
    kpi_row1[1].metric("GEX", "$1.8B", "🟢 STABILE")
    kpi_row1[2].metric("P/C RATIO", "0.88", "⚪ NEUTRO")
    kpi_row1[3].metric("SKEW", "138.4", "🟢 OK")
    kpi_row1[4].metric("MOVE", "98.2", "🟢 CALMO")
    kpi_row1[5].metric("Δ LIQ. 5D", "+1.25%", "📈 ESPANSIONE")

    kpi_row2 = st.columns(6)
    kpi_row2[0].metric("DXY", "101.40", "🟢 USD DOWN")
    kpi_row2[1].metric("GOLD/OIL", "2.12", "🟢 OK")
    kpi_row2[2].metric("TLT PRICE", "$94.20", "📈 TASSI DOWN")
    kpi_row2[3].metric("XLY/XLP", "1.52", "🟢 RISK-ON")
    kpi_row2[4].metric("SPY/RSP", "3.10", "🟢 SANA")
    kpi_row2[5].metric("CURVA VIX", "14.2 / 16.5", "🟢 CONTANGO")

    st.markdown("---")
    
    # LIVELLO 3: WIDGET ANOMALIE Z-SCORE
    st.subheader("⭐ Anomalie Statistiche Rilevate (Z-Score $\\ge \\pm 2.0$)")
    df_stars = pd.DataFrame({
        "Asset Target": ["Cocoa Futures", "Crude Oil WTI", "PayPal ($PYPL)", "2Y UST Yield"],
        "Asset Class": ["Commodities", "Commodities", "Equities", "Rates"],
        "Z-Score 1Y": [-2.35, +2.15, -2.10, +2.05],
        "Stato Statistico": ["⭐ Oversold / Capitulation", "⭐ Overbought / Eccesso", "⭐ Oversold / Reversal", "⭐ Overbought / Eccesso"],
        "Delta W/W": ["-4.2%", "+3.1%", "-1.5%", "+0.8%"]
    })
    st.dataframe(df_stars, use_container_width=True, hide_index=True)

# ==============================================================================
# PAGINA 2: Z-SCORE & COT LAB
# ==============================================================================
elif nav_selection == "2. Z-Score & COT Lab":
    st.title("📊 Z-Score & Posizionamento Istituzionale (COT)")
    st.caption("Normalizzazione statistica del posizionamento Non-Commercial a 52 e 156 settimane.")
    st.markdown("---")
    
    tab_eq, tab_rates, tab_curr, tab_comm = st.tabs(["Equities", "Rates", "Currencies", "Commodities"])
    
    with tab_eq:
        st.dataframe(pd.DataFrame({
            "Contratto / Strumento": ["E-MINI S&P 500", "NASDAQ-100 MINI", "RUSSELL 2000", "VIX FUTURES"],
            "Exchange": ["CME", "CME", "CME", "CFE"],
            "Net Speculative": [-42500, 18200, -12300, -65000],
            "Delta W/W": ["-3,400", "+1,200", "-540", "+8,900"],
            "Z-Score 1Y": [-1.85, +1.20, -0.95, -2.25],
            "Z-Score 3Y": [-1.40, +1.80, -0.60, -2.10],
            "Status": ["⚪ Standard", "⚪ Standard", "⚪ Standard", "⭐ Oversold"]
        }), use_container_width=True, hide_index=True)
        
    with tab_rates:
        st.info("Mappatura attiva: 10Y UST, 2Y UST, 5Y UST, 30D Fed Funds, SOFR 3M/1M, UST Bonds.")
    with tab_curr:
        st.info("Mappatura attiva: USD Index, EUR, GBP, JPY, AUD, CAD, CHF, NZD, MXN.")
    with tab_comm:
        st.info("Mappatura attiva: Gold, Silver, Crude Oil, Cocoa, Coffee, Copper, Nat Gas, Wheat.")
        
    st.markdown("---")
    st.subheader("📈 Analisi Grafica di Distribuzione (Lazy Loading)")
    sel_chart = st.selectbox("Seleziona Strumento:", ["VIX FUTURES", "E-MINI S&P 500", "Cocoa Futures"])
    
    dates = pd.date_range(end="2026-08-21", periods=100)
    z_mock = np.random.randn(100).cumsum() * 0.15
    fig_cot = go.Figure()
    fig_cot.add_trace(go.Scatter(x=dates, y=z_mock, mode='lines', name="Z-Score 1Y", line=dict(color="#D4AF37", width=2)))
    fig_cot.add_hline(y=2.0, line_dash="dash", line_color="red", annotation_text="+2σ")
    fig_cot.add_hline(y=-2.0, line_dash="dash", line_color="green", annotation_text="-2σ")
    fig_cot.update_layout(template="plotly_dark", height=380, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_cot, use_container_width=True)

# ==============================================================================
# PAGINA 3: QUANT LAB (ARCHIVIO STUDI)
# ==============================================================================
elif nav_selection == "3. Quant Lab (Archivio Studi)":
    st.title("🧪 Quant Lab — Archivio Studi & Statistiche")
    st.caption("Catalogo modulare a plugin. Ogni modulo esegue il calcolo unicamente su richiesta.")
    st.markdown("---")
    
    cs1, cs2 = st.columns([2, 1])
    cs1.text_input("🔍 Cerca studio...", "")
    cs2.selectbox("Filtra Categoria:", ["Tutte", "Statistiche Macro", "Bear Market - Drawdown", "Rendimenti", "Strategie", "200 LEVEL"])
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        with st.container(border=True):
            st.subheader("NON FARM PAYROLLS")
            st.caption("⭐ S&P 500 • Macro")
            st.write("Analisi statistica delle revisioni NFP e performance attesa dell'indice.")
            if st.button("Carica Studio", key="q1"):
                st.info("Calcolo modulo NFP on-demand...")
                
        with st.container(border=True):
            st.subheader("Studio dei DRAWDOWN")
            st.caption("⭐ Descrittiva • Rischio")
            st.write("Mappatura storica di profondità e durata delle correzioni di mercato.")
            if st.button("Carica Studio", key="q2"):
                st.info("Calcolo modulo Drawdown on-demand...")

    with col_b:
        with st.container(border=True):
            st.subheader("Tassi - Inflazione")
            st.caption("⭐ Macro • Tassi")
            st.write("Comportamento S&P 500 in base alla combinazione di tassi e inflazione.")
            if st.button("Carica Studio", key="q3"):
                st.info("Calcolo modulo Tassi on-demand...")
                
        with col_b:
            with st.container(border=True):
                st.subheader("Giorni Consecutivi +/-")
                st.caption("⭐ Rendimenti")
                st.write("Probabilità di inversione statistica su streak di sessioni consecutive.")
                if st.button("Carica Studio", key="q4"):
                    st.info("Calcolo modulo Streak on-demand...")

    with col_c:
        with st.container(border=True):
            st.subheader("200 LEVEL S&P 500")
            st.caption("⭐ Breadth")
            st.write("Rendimento atteso quando la % di titoli sopra SMA 200 tocca livelli critici.")
            if st.button("Carica Studio", key="q5"):
                st.info("Calcolo modulo 200 Level on-demand...")
                
        with st.container(border=True):
            st.subheader("Buy the Dip Engine")
            st.caption("⭐ Strategie")
            st.write("Test di acquisto sistematico post-sessioni di forte ribasso.")
            if st.button("Carica Studio", key="q6"):
                st.info("Calcolo modulo Buy the Dip on-demand...")

# ==============================================================================
# PAGINA 4: PROTOCOL SCREENER & TELEGRAM RADAR
# ==============================================================================
elif nav_selection == "4. Protocol Screener & Telegram":
    st.title("🎯 Protocol Execution & Telegram Radar")
    st.caption("Scansione batch EOD e invio notifiche su canale Telegram dedicato.")
    st.markdown("---")
    
    st.subheader("⚙️ Configurazione Protocolli Attivi")
    p_col1, p_col2, p_col3 = st.columns(3)
    p_col1.checkbox("Protocollo 1: POC Capitulation (Bottom Hunter)", value=True)
    p_col2.checkbox("Protocollo 2: Rounding Base & Breakout", value=True)
    p_col3.checkbox("Filtro Z-Score <= -2.0 (⭐)", value=True)
    
    st.markdown("---")
    
    st.subheader("📋 Universo di Scansione")
    st.selectbox("Watchlist Target:", ["S&P 500", "NASDAQ 100", "Watchlist Personale"])
    
    if st.button("🚀 ESEGUI SCANSIONE BATCH EOD"):
        with st.spinner("Scansione quantitativa EOD in esecuzione..."):
            st.success("Scansione completata. 2 Titoli confermati per l'alert.")
            
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
    
    st.markdown("---")
    st.subheader("🔬 Mock Visuale: POC Scanner ($PYPL)")
    
    vp_c1, vp_c2 = st.columns([3, 1])
    with vp_c1:
        x_dates = pd.date_range(end="2026-08-21", periods=150)
        y_prices = np.linspace(310, 61.66, 150) + np.random.randn(150)*4
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=x_dates, y=y_prices, mode='lines', name="Prezzo Close", line=dict(color="#00D1FF")))
        fig_p.add_hline(y=59.81, line_dash="dash", line_color="#A855F7", annotation_text="POC (ATH->Oggi): $59.81")
        fig_p.add_hline(y=40.01, line_dash="dash", line_color="#22C55E", annotation_text="POC (Start->ATH): $40.01")
        fig_p.update_layout(template="plotly_dark", height=380, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_p, use_container_width=True)
        
    with vp_c2:
        bins = np.linspace(40, 310, 30)
        vols = np.exp(-((bins - 60)/45)**2) * 100
        fig_v = go.Figure(go.Bar(x=vols, y=bins, orientation='h', marker_color="#A855F7"))
        fig_v.update_layout(template="plotly_dark", height=380, margin=dict(l=10, r=10, t=30, b=20), xaxis_title="Vol (norm)")
        st.plotly_chart(fig_v, use_container_width=True)
