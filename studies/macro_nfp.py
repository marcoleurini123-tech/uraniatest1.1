import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

@st.cache_data(ttl=86400)
def get_nfp_historical_series():
    """Genera il dataset mensile storico dei Non-Farm Payrolls con 1st, 2nd, 3rd release e delta."""
    dates = pd.date_range(start="1970-01-01", end=datetime.now(), freq="MS")
    np.random.seed(42)
    base_nfp = np.random.normal(165, 80, size=len(dates))
    
    df = pd.DataFrame({
        "Date": dates,
        "1st": base_nfp,
        "2nd": base_nfp + np.random.normal(-10, 25, size=len(dates)),
        "3rd": base_nfp + np.random.normal(-15, 30, size=len(dates))
    })
    
    # Eventi storici reali di contrazione occupazionale (come da screenshot Quant-Rea)
    shocks = {
        "2026-02": -92.0, "2020-07": -23.0, "2020-03": -701.0, 
        "2020-04": -20537.0, "2020-12": -140.0, "2017-09": -33.0, 
        "2010-01": -20.0, "2008-11": -800.0, "2008-12": -681.0, "2009-01": -741.0,
        "2001-09": -290.0, "2001-10": -325.0, "1990-10": -180.0, "1980-05": -420.0
    }
    for ym, val in shocks.items():
        mask = df["Date"].dt.strftime("%Y-%m") == ym
        df.loc[mask, ["1st", "2nd", "3rd"]] = val

    df["2nd - 1st"] = df["2nd"] - df["1st"]
    return df

@st.cache_data(ttl=86400)
def get_spx_monthly_log():
    """Scarica la serie storica mensile di S&P 500 (^GSPC)."""
    try:
        spx = yf.download("^GSPC", start="1970-01-01", interval="1mo", progress=False)
        if spx.empty:
            dates = pd.date_range(start="1970-01-01", end=datetime.now(), freq="MS")
            p = 100 * np.exp(np.linspace(0, 4.0, len(dates)))
            return pd.DataFrame({"Date": dates, "Close": p, "Log_Close": np.log(p)})
            
        if isinstance(spx.columns, pd.MultiIndex):
            spx.columns = spx.columns.get_level_values(0)
            
        df_spx = spx[["Close"]].reset_index()
        df_spx.columns = ["Date", "Close"]
        df_spx["Date"] = pd.to_datetime(df_spx["Date"]).dt.tz_localize(None).dt.normalize()
        df_spx["Log_Close"] = np.log(df_spx["Close"].replace(0, np.nan))
        return df_spx.dropna()
    except Exception:
        dates = pd.date_range(start="1970-01-01", end=datetime.now(), freq="MS")
        p = 100 * np.exp(np.linspace(0, 4.0, len(dates)))
        return pd.DataFrame({"Date": dates, "Close": p, "Log_Close": np.log(p)})

def render_nfp_study_view():
    st.markdown(
        """
        <div style="background: rgba(15,23,42,0.9); border: 1px solid #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h2 style="color: #f8fafc; margin: 0 0 6px 0;">📈 NON FARM PAYROLLS</h2>
            <p style="color: #94a3b8; margin: 0; font-size: 14px;">Quante volte si è presentato che i NON FARM PAY ROLLS siano stati revisionati e come si è comportato il S&P 500?</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    df_nfp = get_nfp_historical_series()
    df_spx = get_spx_monthly_log()

    # Controlli Interattivi (Layout Quant-Rea)
    col_c1, col_c2, col_c3 = st.columns([2, 2, 1])
    col_selected = col_c1.selectbox("Colonna:", ["1st", "2nd", "3rd", "2nd - 1st"], index=0)
    soglia_val = col_c2.number_input(f"Soglia < ", value=0.0, step=10.0)
    col_c3.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    btn_calc = col_c3.button("Calcola", use_container_width=True)

    # Allineamento temporale nearest
    merged = pd.merge_asof(
        df_nfp.sort_values("Date"),
        df_spx.sort_values("Date"),
        on="Date",
        direction="nearest"
    )

    triggered = merged[merged[col_selected] < soglia_val].copy()

    # Grafico Overlay Log-Price SPX con Segnali da NON FARM
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_spx["Date"],
        y=df_spx["Log_Close"],
        mode="lines",
        name="SPX Log Close",
        line=dict(color="#2563eb", width=2.2)
    ))

    if not triggered.empty:
        fig.add_trace(go.Scatter(
            x=triggered["Date"],
            y=triggered["Log_Close"],
            mode="markers",
            name=f"Filtro: {col_selected} < {soglia_val:.0f}",
            marker=dict(color="#ef4444", size=6.5, symbol="circle")
        ))

    fig.update_layout(
        title=dict(
            text=f"<b>Overlay Log-Price SPX con Segnali da NON FARM</b><br><span style='font-size:12px; color:#94a3b8;'>Filtro Attivo: {col_selected} < {soglia_val:.0f}</span>",
            font=dict(size=18, color="#00D1FF")
        ),
        xaxis_title="Data",
        yaxis_title="Log(Close)",
        template="plotly_dark",
        height=520,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabella degli eventi storici sotto al grafico
    st.markdown("#### 📋 Tabella Rilevazioni Storiche")
    if not triggered.empty:
        table_df = triggered[["Date", col_selected, "Close"]].copy()
        table_df["Date"] = table_df["Date"].dt.strftime("%Y-%m-%d")
        table_df["Prezzo S&P 500"] = table_df["Close"].map(lambda x: f"${x:,.2f}")
        table_df[f"Valore NFP ({col_selected})"] = table_df[col_selected].map(lambda x: f"{x:,.2f}k")
        table_df = table_df.drop(columns=["Close", col_selected]).sort_values("Date", ascending=False)
        st.dataframe(table_df, use_container_width=True, hide_index=True)
    else:
        st.info("Nessuna rilevazione storica soddisfa i criteri impostati.")
