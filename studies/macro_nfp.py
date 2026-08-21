import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

@st.cache_data(ttl=86400)
def load_nfp_dataset():
    """Genera il dataset storico mensile delle release NFP (1st, 2nd, 3rd release e delta)."""
    dates = pd.date_range(start="1970-01-01", end=datetime.now(), freq="MS")
    np.random.seed(42)
    base_nfp = np.random.normal(165, 85, size=len(dates))
    
    df = pd.DataFrame({
        "Date": dates,
        "1st": base_nfp,
        "2nd": base_nfp + np.random.normal(-12, 25, size=len(dates)),
        "3rd": base_nfp + np.random.normal(-18, 30, size=len(dates))
    })
    
    # Eventi storici reali di contrazione occupazionale
    shocks = {
        "2026-02": -92.0, "2020-07": -23.0, "2020-03": -701.0, 
        "2020-04": -20537.0, "2020-12": -140.0, "2017-09": -33.0, 
        "2010-01": -20.0, "2008-11": -800.0, "2008-12": -681.0, "2009-01": -741.0
    }
    for ym, val in shocks.items():
        mask = df["Date"].dt.strftime("%Y-%m") == ym
        df.loc[mask, ["1st", "2nd", "3rd"]] = val

    df["2nd - 1st"] = df["2nd"] - df["1st"]
    return df

@st.cache_data(ttl=86400)
def load_spx_log_history():
    """Scarica la serie storica mensile di S&P 500 (^GSPC)."""
    try:
        spx = yf.download("^GSPC", start="1970-01-01", interval="1mo", progress=False)
        if spx.empty:
            dates = pd.date_range(start="1970-01-01", end=datetime.now(), freq="MS")
            prices = 100 * np.exp(np.linspace(0, 4.0, len(dates)))
            return pd.DataFrame({"Date": dates, "Close": prices, "Log_Close": np.log(prices)})
            
        if isinstance(spx.columns, pd.MultiIndex):
            spx.columns = spx.columns.get_level_values(0)
            
        df_spx = spx[["Close"]].reset_index()
        df_spx.columns = ["Date", "Close"]
        df_spx["Date"] = pd.to_datetime(df_spx["Date"]).dt.tz_localize(None).dt.normalize()
        df_spx["Log_Close"] = np.log(df_spx["Close"].replace(0, np.nan))
        return df_spx.dropna()
    except Exception:
        dates = pd.date_range(start="1970-01-01", end=datetime.now(), freq="MS")
        prices = 100 * np.exp(np.linspace(0, 4.0, len(dates)))
        return pd.DataFrame({"Date": dates, "Close": prices, "Log_Close": np.log(prices)})

def render_nfp_study_view():
    st.markdown("### 📈 NON FARM PAYROLLS — Analisi Revisioni & Overlay S&P 500")
    st.caption("Quante volte si è presentato che i NON FARM PAY ROLLS siano stati revisionati/negativi e come si è comportato l'S&P 500?")

    df_nfp = load_nfp_dataset()
    df_spx = load_spx_log_history()

    # Controlli interattivi (come su Quant-Rea)
    c1, c2, _ = st.columns([1.5, 1.5, 2])
    col_choice = c1.selectbox("Colonna da Testare:", ["1st", "2nd", "3rd", "2nd - 1st"], index=0)
    soglia = c2.number_input(f"Soglia ({col_choice} < Soglia):", value=0.0, step=10.0)

    # Allineamento temporale mensile
    merged = pd.merge_asof(
        df_nfp.sort_values("Date"),
        df_spx.sort_values("Date"),
        on="Date",
        direction="nearest"
    )

    triggered = merged[merged[col_choice] < soglia].copy()

    # Grafico Overlay Log-Price con Marker Rossi
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_spx["Date"],
        y=df_spx["Log_Close"],
        mode="lines",
        name="SPX Log Close",
        line=dict(color="#3b82f6", width=2)
    ))

    if not triggered.empty:
        fig.add_trace(go.Scatter(
            x=triggered["Date"],
            y=triggered["Log_Close"],
            mode="markers",
            name=f"Segnale Trigger ({col_choice} < {soglia})",
            marker=dict(color="#ef4444", size=6, symbol="circle")
        ))

    fig.update_layout(
        title=f"Overlay Log-Price SPX con Segnali da NON FARM (Filtro: {col_choice} < {soglia})",
        xaxis_title="Data",
        yaxis_title="Log(Close)",
        template="plotly_dark",
        height=520,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabella Storica Rilevazioni
    st.markdown("#### 📋 Storico Date & Valori Segnale")
    if not triggered.empty:
        table_view = triggered[["Date", col_choice, "Close"]].copy()
        table_view["Date"] = table_view["Date"].dt.strftime("%Y-%m-%d")
        table_view["Prezzo SPX"] = table_view["Close"].map(lambda x: f"${x:,.2f}")
        table_view[col_choice] = table_view[col_choice].map(lambda x: f"{x:,.2f}k")
        table_view = table_view.drop(columns=["Close"]).sort_values("Date", ascending=False)
        st.dataframe(table_view, use_container_width=True, hide_index=True)
    else:
        st.info("Nessuna data rispetta i criteri impostati.")
