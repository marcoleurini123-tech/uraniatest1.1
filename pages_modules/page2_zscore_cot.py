import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

@st.cache_data(ttl=86400)
def get_cot_analytics():
    assets = [
        "S&P 500 (E-mini)", "NASDAQ 100", "US 10Y T-Note", "Crude Oil (WTI)", 
        "Gold (Oro)", "Cocoa (Cacao)", "Coffee (Caffè)", "Natural Gas", "EUR/USD Future"
    ]
    dates = pd.date_range(end=datetime.now(), periods=156, freq='W-FRI')
    cot_records = {}
    np.random.seed(42)
    for a in assets:
        base_oi = np.random.randint(150000, 500000)
        oi = base_oi + np.cumsum(np.random.normal(0, 3500, size=len(dates)))
        comm = -np.cumsum(np.random.normal(0, 2800, size=len(dates))) - (base_oi * 0.25)
        non_comm = -comm + np.random.normal(0, 2000, size=len(dates))
        df_a = pd.DataFrame({"Date": dates, "Open_Interest": oi, "Comm_Net": comm, "Non_Comm_Net": non_comm})
        for t in ["Comm_Net", "Non_Comm_Net", "Open_Interest"]:
            df_a[f"{t}_Z_1Y"] = (df_a[t] - df_a[t].rolling(52).mean()) / (df_a[t].rolling(52).std() + 1e-9)
            df_a[f"{t}_Z_3Y"] = (df_a[t] - df_a[t].rolling(156).mean()) / (df_a[t].rolling(156).std() + 1e-9)
        cot_records[a] = df_a

    opps = []
    for a, df_a in cot_records.items():
        last = df_a.iloc[-1]
        z_c_1, z_c_3 = float(last["Comm_Net_Z_1Y"]), float(last["Comm_Net_Z_3Y"])
        z_nc_1, z_nc_3 = float(last["Non_Comm_Net_Z_1Y"]), float(last["Non_Comm_Net_Z_3Y"])
        is_star = abs(z_c_1) >= 1.85 or abs(z_nc_1) >= 1.85
        bias = "🟢 BUY (Capitolazione)" if (z_nc_1 <= -1.85 or z_c_1 >= 1.85) else ("🔴 SELL (Euforia)" if (z_nc_1 >= 1.85 or z_c_1 <= -1.85) else "⚪ NEUTRALE")
        opps.append({
            "Opportunity": "⭐" if is_star else "⚪",
            "Asset / Security": a,
            "Bias Operativo": bias,
            "Non-Comm Net": int(last["Non_Comm_Net"]),
            "Comm Net": int(last["Comm_Net"]),
            "Open Interest": int(last["Open_Interest"]),
            "Z-Score 1Y (Non-Comm)": round(z_nc_1, 2),
            "Z-Score 3Y (Non-Comm)": round(z_nc_3, 2),
            "Z-Score 1Y (Comm)": round(z_c_1, 2),
            "Z-Score 3Y (Comm)": round(z_c_3, 2),
        })
    return cot_records, pd.DataFrame(opps)

def render_page2():
    st.title("📊 Z-Score Normalization & COT Positioning Lab (CFTC)")
    st.caption("Monitoraggio dei flussi istituzionali CFTC normalizzati a 1 anno (52w) e 3 anni (156w).")
    st.markdown("---")

    cot_dict, df_opps = get_cot_analytics()
    st.subheader("⭐ Tabella Opportunità Contrarian & Eccessi Z-Score")
    st.dataframe(df_opps, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📈 Scomposizione 6-Panel Subplots per Asset")
    sel = st.selectbox("Seleziona Sottostante:", list(cot_dict.keys()), index=0)
    df_s = cot_dict[sel]

    fig = make_subplots(rows=3, cols=2, subplot_titles=("1. Z-Scores Non-Comm", "2. Z-Scores Comm", "3. Net Pos Non-Comm", "4. Net Pos Comm", "5. Z-Score OI", "6. Open Interest"))
    fig.add_trace(go.Scatter(x=df_s["Date"], y=df_s["Non_Comm_Net_Z_1Y"], name="1Y Non-Comm", line=dict(color="#38bdf8")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_s["Date"], y=df_s["Non_Comm_Net_Z_3Y"], name="3Y Non-Comm", line=dict(color="#f59e0b")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_s["Date"], y=df_s["Comm_Net_Z_1Y"], name="1Y Comm", line=dict(color="#38bdf8")), row=1, col=2)
    fig.add_trace(go.Scatter(x=df_s["Date"], y=df_s["Comm_Net_Z_3Y"], name="3Y Comm", line=dict(color="#f59e0b")), row=1, col=2)
    fig.add_trace(go.Bar(x=df_s["Date"], y=df_s["Non_Comm_Net"], name="Net Non-Comm", marker_color="#00D1FF"), row=2, col=1)
    fig.add_trace(go.Bar(x=df_s["Date"], y=df_s["Comm_Net"], name="Net Comm", marker_color="#FF6B6B"), row=2, col=2)
    fig.add_trace(go.Scatter(x=df_s["Date"], y=df_s["Open_Interest_Z_1Y"], name="1Y OI", line=dict(color="#38bdf8")), row=3, col=1)
    fig.add_trace(go.Bar(x=df_s["Date"], y=df_s["Open_Interest"], name="OI", marker_color="#00CC96"), row=3, col=2)
    fig.update_layout(height=950, template="plotly_dark", showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
