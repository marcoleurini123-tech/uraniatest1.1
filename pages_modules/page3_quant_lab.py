import streamlit as st

def render_page3():
    st.title("🔬 Quant Lab: Studi Storici, Probabilità & Metriche (Massimo Rea)")
    st.caption("Archivio proprietario dei paper quantitativi e matrici statistiche EOD.")
    st.markdown("---")

    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown("""<div style="background:#0b1320; border:1px solid #1e293b; border-radius:12px; padding:20px;"><h4 style="color:#00b4d8; margin:0 0 8px 0;">Studio 01: POC Capitulation Edge</h4><p style="font-size:12px; color:#94a3b8;">Probabilità di rimbalzo su titoli in drawdown > 40% dopo compressione volumetrica sul POC.</p><div style="font-weight:800; color:#10b981; font-size:18px;">Win Rate: 71.4%</div><small style="color:#64748b;">Campione: 450 trade EOD (2012–2026)</small></div>""", unsafe_allow_html=True)
    with q2:
        st.markdown("""<div style="background:#0b1320; border:1px solid #1e293b; border-radius:12px; padding:20px;"><h4 style="color:#38bdf8; margin:0 0 8px 0;">Studio 02: Zero-Cost Collar & Theta</h4><p style="font-size:12px; color:#94a3b8;">Efficienza di protezione del capitale su portafogli azionari durante le fasi di Stagflazione con Covered Call.</p><div style="font-weight:800; color:#38bdf8; font-size:18px;">Max DD: -5.2%</div><small style="color:#64748b;">Copertura: 94.2% del delta</small></div>""", unsafe_allow_html=True)
    with q3:
        st.markdown("""<div style="background:#0b1320; border:1px solid #1e293b; border-radius:12px; padding:20px;"><h4 style="color:#f59e0b; margin:0 0 8px 0;">Studio 03: Net Fed Liquidity Lag</h4><p style="font-size:12px; color:#94a3b8;">Correlazione temporale con lag a 10 giorni tra le iniezioni di liquidità netta Fed e multipli S&P 500.</p><div style="font-weight:800; color:#f59e0b; font-size:18px;">Correlazione: +0.82</div><small style="color:#64748b;">Analisi rolling a 250gg</small></div>""", unsafe_allow_html=True)
