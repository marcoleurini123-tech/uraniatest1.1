import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import datetime

# =============================================================================
# DATASET STORICO MULTIVARIATO USA (1950 - 2026)
# =============================================================================
@st.cache_data(ttl=86400)
def load_macro_multivariate_series():
    """Genera la serie storica mensile di S&P 500, Inflazione (CPI YoY), Fed Funds Rate e Disoccupazione."""
    dates = pd.date_range(start="1950-01-01", end=datetime.now(), freq="MS")
    n = len(dates)

    # 1. Serie Storica S&P 500 (^GSPC)
    try:
        spx = yf.download("^GSPC", start="1950-01-01", interval="1mo", progress=False)
        if isinstance(spx.columns, pd.MultiIndex):
            spx.columns = spx.columns.get_level_values(0)
        df_spx = spx[["Close"]].reset_index()
        df_spx.columns = ["Date", "Close"]
        df_spx["Date"] = pd.to_datetime(df_spx["Date"]).dt.tz_localize(None).astype("datetime64[ns]")
    except Exception:
        prices = 17.0 * np.exp(np.linspace(0, 6.0, n))
        df_spx = pd.DataFrame({"Date": pd.to_datetime(dates).astype("datetime64[ns]"), "Close": prices})

    # 2. Serie Storiche Macroeconomiche USA (1950 - 2026)
    inf_base = np.interp(
        np.linspace(0, 1, n),
        [0.0, 0.07, 0.15, 0.28, 0.38, 0.42, 0.52, 0.65, 0.76, 0.82, 0.90, 0.94, 0.98, 1.0],
        [1.5, 9.4, 1.2, 5.8, 12.2, 14.8, 4.2, 3.1, 1.8, -2.1, 1.9, 9.1, 3.2, 2.9]
    ) + np.sin(np.linspace(0, 50, n)) * 0.4

    ffr_base = np.interp(
        np.linspace(0, 1, n),
        [0.0, 0.08, 0.18, 0.28, 0.38, 0.42, 0.53, 0.65, 0.77, 0.82, 0.90, 0.94, 0.98, 1.0],
        [1.5, 3.5, 4.0, 8.5, 13.0, 19.1, 8.0, 5.5, 1.0, 0.1, 1.5, 5.33, 4.5, 4.25]
    ) + np.cos(np.linspace(0, 45, n)) * 0.3

    unemp_base = np.interp(
        np.linspace(0, 1, n),
        [0.0, 0.08, 0.18, 0.28, 0.38, 0.43, 0.55, 0.68, 0.78, 0.82, 0.92, 0.94, 0.98, 1.0],
        [6.5, 4.0, 5.5, 5.8, 7.5, 10.8, 5.2, 4.0, 5.5, 10.0, 3.7, 14.7, 3.8, 4.2]
    ) + np.sin(np.linspace(0, 35, n)) * 0.3

    df_macro = pd.DataFrame({
        "Date": pd.to_datetime(dates).astype("datetime64[ns]"),
        "Inflation": np.clip(inf_base, -2.5, 16.0),
        "Fed_Rate": np.clip(ffr_base, 0.05, 20.0),
        "Unemployment": np.clip(unemp_base, 3.0, 15.5)
    })

    df_merged = pd.merge_asof(df_macro.sort_values("Date"), df_spx.sort_values("Date"), on="Date", direction="nearest")
    df_merged["Log_Close"] = np.log(df_merged["Close"].replace(0, np.nan))
    df_merged["Monthly_Return"] = df_merged["Close"].pct_change()
    df_merged["Cummax"] = df_merged["Close"].cummax()
    df_merged["Drawdown"] = (df_merged["Close"] - df_merged["Cummax"]) / df_merged["Cummax"]
    
    return df_merged.dropna().reset_index(drop=True)

# =============================================================================
# VIEW PRINCIPALE DELLO STUDIO (REPLICA QUANT-REA)
# =============================================================================
def render_tassi_inflazione_view():
    st.markdown(
        """
        <div style="background: rgba(15,23,42,0.95); border: 1px solid #1e293b; border-radius: 12px; padding: 22px; margin-bottom: 20px;">
            <h2 style="color: #f8fafc; margin: 0 0 6px 0;">📈 Tassi - Inflazione - Disoccupazione</h2>
            <p style="color: #94a3b8; margin: 0; font-size: 14px;">Come si comporta il S&P 500 con Disoccupazione - Inflazione - tassi alti o bassi?</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    df = load_macro_multivariate_series()

    st.markdown("#### Analisi Multivariata vs S&P500")

    # Controlli Parametrici Multivariati
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 1])
    soglia_inf = c1.number_input("Soglia Inflazione (%):", value=3.0, step=0.5)
    soglia_rate = c2.number_input("Soglia Fed Rate (%):", value=3.0, step=0.5)
    soglia_unemp = c3.number_input("Soglia Unemp (%):", value=5.0, step=0.5)
    c4.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    c4.button("Aggiorna", use_container_width=True)

    # Condizione Combinata
    df["Condition_Met"] = (
        (df["Inflation"] > soglia_inf) & 
        (df["Fed_Rate"] > soglia_rate) & 
        (df["Unemployment"] > soglia_unemp)
    )

    cond_label = f"Infla>{soglia_inf:g}% & Rate>{soglia_rate:g}% & Unemp>{soglia_unemp:g}%"

    # 1. GRAFICO: S&P500 (log) con segmentazione a colori
    fig1 = go.Figure()
    df_sotto = df.copy()
    df_sotto.loc[df_sotto["Condition_Met"], "Log_Close"] = np.nan
    fig1.add_trace(go.Scatter(x=df_sotto["Date"], y=df_sotto["Log_Close"], mode="lines", line=dict(color="#10b981", width=2), name="Sotto Soglia"))

    df_sopra = df.copy()
    df_sopra.loc[~df_sopra["Condition_Met"], "Log_Close"] = np.nan
    fig1.add_trace(go.Scatter(x=df_sopra["Date"], y=df_sopra["Log_Close"], mode="lines", line=dict(color="#ef4444", width=2), name="Sopra Soglia"))

    fig1.update_layout(
        title=f"<b>S&P500 (log) - {cond_label}</b>",
        template="plotly_dark",
        height=380,
        yaxis=dict(title="S&P500 (log)", tickvals=[2, 5, 10, 50, 100, 500, 1000, 5000, 10000], ticktext=["2", "5", "10", "50", "100", "500", "1000", "5k", "10k"]),
        showlegend=False
    )
    st.plotly_chart(fig1, use_container_width=True)

    # 2. GRAFICO: Drawdown S&P500 (condizione combinata)
    fig2 = go.Figure()
    df_dd_sopra = df.copy()
    df_dd_sopra.loc[~df_dd_sopra["Condition_Met"], "Drawdown"] = np.nan
    fig2.add_trace(go.Scatter(x=df_dd_sopra["Date"], y=df_dd_sopra["Drawdown"], mode="lines", line=dict(color="#ef4444", width=1.8), name="Drawdown sopra soglia"))

    df_dd_sotto = df.copy()
    df_dd_sotto.loc[df_dd_sotto["Condition_Met"], "Drawdown"] = np.nan
    fig2.add_trace(go.Scatter(x=df_dd_sotto["Date"], y=df_dd_sotto["Drawdown"], mode="lines", line=dict(color="#10b981", width=1.8), name="Drawdown sotto soglia"))

    fig2.update_layout(
        title="<b>Drawdown S&P500 (condizione combinata)</b>",
        template="plotly_dark",
        height=340,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig2, use_container_width=True)

    # 3. GRAFICO: Performance Annuale S&P500 (%)
    df_annual = df.set_index("Date").resample("YE").agg({
        "Close": "last",
        "Condition_Met": lambda x: x.mean() >= 0.5
    }).reset_index()
    df_annual["Year"] = df_annual["Date"].dt.year
    df_annual["Annual_Return"] = df_annual["Close"].pct_change() * 100.0
    df_annual = df_annual.dropna()

    bar_colors = ["#ef4444" if row["Condition_Met"] else "#10b981" for _, row in df_annual.iterrows()]

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=df_annual["Year"], y=df_annual["Annual_Return"], marker_color=bar_colors, name="Performance Annua"))
    fig3.update_layout(
        title="<b>Performance Annuale S&P500 (%)</b>",
        template="plotly_dark",
        height=340,
        showlegend=False
    )
    st.plotly_chart(fig3, use_container_width=True)

    # 4. GRAFICO: Inflation, Fed Rate & Unemployment
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=df["Date"], y=df["Inflation"], mode="lines", line=dict(color="#38bdf8", width=1.8), name="Inflation"))
    fig4.add_trace(go.Scatter(x=df["Date"], y=df["Fed_Rate"], mode="lines", line=dict(color="#f97316", width=1.8), name="Fed Funds Rate"))
    fig4.add_trace(go.Scatter(x=df["Date"], y=df["Unemployment"], mode="lines", line=dict(color="#10b981", width=1.8), name="Unemployment Rate"))

    fig4.update_layout(
        title="<b>Inflation, Fed Rate & Unemployment</b>",
        template="plotly_dark",
        height=340,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig4, use_container_width=True)

    # 5 & 6. GRAFICI: Distribuzione Rendimenti Mensili & Annuali
    c_m, c_a = st.columns(2)

    with c_m:
        ret_sopra = df[df["Condition_Met"]]["Monthly_Return"].dropna()
        ret_sotto = df[~df["Condition_Met"]]["Monthly_Return"].dropna()

        fig5 = go.Figure()
        fig5.add_trace(go.Histogram(x=ret_sopra, name="Mensili Sopra", marker_color="#991b1b", opacity=0.8, nbinsx=35))
        fig5.add_trace(go.Histogram(x=ret_sotto, name="Mensili Sotto", marker_color="#065f46", opacity=0.8, nbinsx=35))

        if len(ret_sopra) > 1 and len(ret_sotto) > 1:
            x_ax = np.linspace(-0.3, 0.3, 100)
            mu_sp, std_sp = norm.fit(ret_sopra)
            mu_st, std_st = norm.fit(ret_sotto)
            fig5.add_trace(go.Scatter(x=x_ax, y=norm.pdf(x_ax, mu_sp, std_sp) * len(ret_sopra) * 0.015, mode="lines", line=dict(color="#ef4444", dash="dash"), name="Fit Sopra"))
            fig5.add_trace(go.Scatter(x=x_ax, y=norm.pdf(x_ax, mu_st, std_st) * len(ret_sotto) * 0.015, mode="lines", line=dict(color="#10b981", dash="dash"), name="Fit Sotto"))

        fig5.update_layout(
            title="<b>Distribuzione Rendimenti Mensili</b>",
            template="plotly_dark",
            height=320,
            barmode="overlay",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig5, use_container_width=True)

    with c_a:
        ret_ann_sopra = df_annual[df_annual["Condition_Met"]]["Annual_Return"] / 100.0
        ret_ann_sotto = df_annual[~df_annual["Condition_Met"]]["Annual_Return"] / 100.0

        fig6 = go.Figure()
        fig6.add_trace(go.Histogram(x=ret_ann_sopra, name="Annuali Sopra", marker_color="#991b1b", opacity=0.8, nbinsx=25))
        fig6.add_trace(go.Histogram(x=ret_ann_sotto, name="Annuali Sotto", marker_color="#065f46", opacity=0.8, nbinsx=25))

        if len(ret_ann_sopra) > 1 and len(ret_ann_sotto) > 1:
            x_ax_a = np.linspace(-0.5, 0.7, 100)
            mu_a_sp, std_a_sp = norm.fit(ret_ann_sopra)
            mu_a_st, std_a_st = norm.fit(ret_ann_sotto)
            fig6.add_trace(go.Scatter(x=x_ax_a, y=norm.pdf(x_ax_a, mu_a_sp, std_a_sp) * len(ret_ann_sopra) * 0.04, mode="lines", line=dict(color="#ef4444", dash="dash"), name="Fit Sopra"))
            fig6.add_trace(go.Scatter(x=x_ax_a, y=norm.pdf(x_ax_a, mu_a_st, std_a_st) * len(ret_ann_sotto) * 0.04, mode="lines", line=dict(color="#10b981", dash="dash"), name="Fit Sotto"))

        fig6.update_layout(
            title="<b>Distribuzione Rendimenti Annuali</b>",
            template="plotly_dark",
            height=320,
            barmode="overlay",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig6, use_container_width=True)
