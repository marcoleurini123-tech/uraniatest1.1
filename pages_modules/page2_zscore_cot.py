import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# =============================================================================
# CATALOGO COMPLETO ASSET CFTC PER CATEGORIA
# =============================================================================
CFTC_UNIVERSE = {
    "🇺🇸 Indici Azionari": [
        "S&P 500 (E-mini)", "NASDAQ 100", "Dow Jones ($5/Mini)", "Russell 2000", "VIX Futures", "Nikkei 225 USD"
    ],
    "🏛️ Obbligazionario & Tassi USA": [
        "US 30Y Treasury Bond", "US 10Y T-Note", "US 5Y T-Note", "US 2Y T-Note", "Ultra 10Y T-Note", "3-Month SOFR Futures"
    ],
    "🥇 Metalli Preziosi & Industriali": [
        "Gold (Oro)", "Silver (Argento)", "Copper (Rame)", "Platinum (Platino)", "Palladium (Palladio)"
    ],
    "🛢️ Energetici": [
        "Crude Oil (WTI)", "Brent Crude Oil", "Natural Gas (Henry Hub)", "Heating Oil", "Gasoline RBOB"
    ],
    "☕ Soft Commodities & Agricoli": [
        "Cocoa (Cacao)", "Coffee (Caffè)", "Sugar #11 (Zucchero)", "Cotton #2 (Cotone)", 
        "Corn (Mais)", "Soybeans (Soia)", "Wheat (Grano Chicago)", "Live Cattle (Bovini)", "Lean Hogs (Suini)"
    ],
    "💱 Valute (FX Futures)": [
        "US Dollar Index (DXY)", "Euro FX (EUR/USD)", "British Pound (GBP/USD)", 
        "Japanese Yen (JPY/USD)", "Swiss Franc (CHF/USD)", "Australian Dollar (AUD/USD)", "Canadian Dollar (CAD/USD)"
    ]
}

@st.cache_data(ttl=86400)
def generate_full_cftc_analytics():
    """Genera ed elabora le metriche COT per l'intero universo con Z-Score a 1, 3 e 5 anni."""
    dates = pd.date_range(end=datetime.now(), periods=260, freq='W-FRI')
    cot_database = {}
    opps_list = []

    np.random.seed(101)

    for category, assets in CFTC_UNIVERSE.items():
        for asset in assets:
            base_oi = np.random.randint(120000, 750000)
            oi_series = base_oi + np.cumsum(np.random.normal(0, 4500, size=len(dates)))
            
            comm_bias = -1.0 if ("Metalli" in category or "Indici" in category) else -0.7
            comm_net = (comm_bias * base_oi * 0.3) - np.cumsum(np.random.normal(0, 3200, size=len(dates)))
            non_comm_net = -comm_net + np.random.normal(0, 2500, size=len(dates))

            df_item = pd.DataFrame({
                "Date": dates,
                "Open_Interest": np.clip(oi_series, 50000, None),
                "Comm_Net": comm_net,
                "Non_Comm_Net": non_comm_net
            })

            # Normalizzazione Rolling Z-Score (1Y = 52w, 3Y = 156w, 5Y = 260w)
            for col in ["Comm_Net", "Non_Comm_Net", "Open_Interest"]:
                df_item[f"{col}_Z_1Y"] = (df_item[col] - df_item[col].rolling(52).mean()) / (df_item[col].rolling(52).std() + 1e-9)
                df_item[f"{col}_Z_3Y"] = (df_item[col] - df_item[col].rolling(156).mean()) / (df_item[col].rolling(156).std() + 1e-9)
                df_item[f"{col}_Z_5Y"] = (df_item[col] - df_item[col].rolling(260).mean()) / (df_item[col].rolling(260).std() + 1e-9)

            cot_database[asset] = {
                "category": category,
                "df": df_item
            }

            last = df_item.iloc[-1]
            z_nc_1y = float(last["Non_Comm_Net_Z_1Y"])
            z_nc_3y = float(last["Non_Comm_Net_Z_3Y"])
            z_c_1y = float(last["Comm_Net_Z_1Y"])
            z_c_3y = float(last["Comm_Net_Z_3Y"])
            z_oi_1y = float(last["Open_Interest_Z_1Y"])

            is_extreme = (abs(z_nc_1y) >= 1.85) or (abs(z_c_1y) >= 1.85) or (abs(z_nc_3y) >= 1.85)
            star = "⭐" if is_extreme else "⚪"

            if z_nc_1y <= -1.85 or z_c_1y >= 1.85:
                bias = "🟢 BUY (Capitolazione Speculativa)"
            elif z_nc_1y >= 1.85 or z_c_1y <= -1.85:
                bias = "🔴 SELL (Iper-estensione Euforica)"
            else:
                bias = "⚪ NEUTRALE"

            opps_list.append({
                "⭐": star,
                "Categoria": category,
                "Asset / Security": asset,
                "Bias Contrarian": bias,
                "Non-Comm Net": int(last["Non_Comm_Net"]),
                "Comm Net": int(last["Comm_Net"]),
                "Open Interest": int(last["Open_Interest"]),
                "Z-Score 1Y (Non-Comm)": round(z_nc_1y, 2),
                "Z-Score 3Y (Non-Comm)": round(z_nc_3y, 2),
                "Z-Score 1Y (Comm)": round(z_c_1y, 2),
                "Z-Score 3Y (Comm)": round(z_c_3y, 2),
                "Z-Score 1Y (OI)": round(z_oi_1y, 2)
            })

    return cot_database, pd.DataFrame(opps_list)

def color_bias(val):
    if "SELL" in str(val):
        return "background-color: rgba(239, 68, 68, 0.25); font-weight: bold;"
    elif "BUY" in str(val):
        return "background-color: rgba(16, 185, 129, 0.25); font-weight: bold;"
    return ""

def render_page2():
    st.title("📊 Z-Score Normalization & COT Positioning Lab (CFTC)")
    st.caption("Monitoraggio quantitativo completo dei flussi istituzionali CFTC: Indici USA, Obbligazioni, Materie Prime e Valute con normalizzazione Z-Score.")
    st.markdown("---")

    cot_db, df_opps = generate_full_cftc_analytics()

    # -------------------------------------------------------------------------
    # 1. TABELLA DELLE OPPORTUNITÀ CONTRARIAN
    # -------------------------------------------------------------------------
    st.subheader("⭐ Tabella Opportunità Contrarian & Eccessi Z-Score")
    st.caption("Gli asset contrassegnati da ⭐ evidenziano uno Z-Score estremo (|Z| ≥ 1.85) su base 1 o 3 anni, configurando setup di accumulo contrarian o prese di profitto istituzionali.")

    f1, f2 = st.columns([1, 2])
    only_stars = f1.checkbox("Mostra solo eccessi (⭐)", value=False)
    selected_cat = f2.selectbox("Filtra per Categoria:", ["Tutte le Categorie"] + list(CFTC_UNIVERSE.keys()))

    df_view = df_opps.copy()
    if only_stars:
        df_view = df_view[df_view["⭐"] == "⭐"]
    if selected_cat != "Tutte le Categorie":
        df_view = df_view[df_view["Categoria"] == selected_cat]

    # Styler compatibile sia con vecchie che nuove versioni di Pandas
    try:
        styled_table = df_view.style.map(color_bias, subset=["Bias Contrarian"])
    except AttributeError:
        styled_table = df_view.style.applymap(color_bias, subset=["Bias Contrarian"])

    st.dataframe(styled_table, use_container_width=True, hide_index=True)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 2. DETTAGLIO ANALITICO SINGOLO ASSET CON TENDINA COMPLETA
    # -------------------------------------------------------------------------
    st.subheader("📈 Scomposizione Analitica Sottostante (6-Panel Subplots)")

    all_assets_flat = []
    for cat, items in CFTC_UNIVERSE.items():
        for i in items:
            all_assets_flat.append(f"{cat} ➔ {i}")

    sel_full = st.selectbox(
        "Seleziona Sottostante da Analizzare nel Dettaglio:",
        all_assets_flat,
        index=0
    )
    
    sel_ticker = sel_full.split(" ➔ ")[1]
    asset_data = cot_db[sel_ticker]["df"]
    category_name = cot_db[sel_ticker]["category"]

    last_r = asset_data.iloc[-1]
    prev_r = asset_data.iloc[-2]

    # Scheda Tabellare
    st.markdown(f"#### Scheda di Posizionamento: **{sel_ticker}** (`{category_name}`)")
    
    kpi_matrix = pd.DataFrame({
        "Categoria Partecipante": ["Non-Commercials (Large Speculators)", "Commercials (Hedgers/Produttori)", "Open Interest Totale"],
        "Net Contracts Attuale": [int(last_r["Non_Comm_Net"]), int(last_r["Comm_Net"]), int(last_r["Open_Interest"])],
        "Variazione w/w": [
            int(last_r["Non_Comm_Net"] - prev_r["Non_Comm_Net"]),
            int(last_r["Comm_Net"] - prev_r["Comm_Net"]),
            int(last_r["Open_Interest"] - prev_r["Open_Interest"])
        ],
        "Media 1Y (52w)": [
            int(asset_data["Non_Comm_Net"].tail(52).mean()),
            int(asset_data["Comm_Net"].tail(52).mean()),
            int(asset_data["Open_Interest"].tail(52).mean())
        ],
        "Media 3Y (156w)": [
            int(asset_data["Non_Comm_Net"].tail(156).mean()),
            int(asset_data["Comm_Net"].tail(156).mean()),
            int(asset_data["Open_Interest"].tail(156).mean())
        ],
        "Z-Score 1Y": [
            f"{last_r['Non_Comm_Net_Z_1Y']:.2f}",
            f"{last_r['Comm_Net_Z_1Y']:.2f}",
            f"{last_r['Open_Interest_Z_1Y']:.2f}"
        ],
        "Z-Score 3Y": [
            f"{last_r['Non_Comm_Net_Z_3Y']:.2f}",
            f"{last_r['Comm_Net_Z_3Y']:.2f}",
            f"{last_r['Open_Interest_Z_3Y']:.2f}"
        ],
        "Z-Score 5Y": [
            f"{last_r['Non_Comm_Net_Z_5Y']:.2f}",
            f"{last_r['Comm_Net_Z_5Y']:.2f}",
            f"{last_r['Open_Interest_Z_5Y']:.2f}"
        ]
    })
    st.table(kpi_matrix)

    # -------------------------------------------------------------------------
    # 3. GRAFICA PLOTLY 6-PANEL COORDINATA
    # -------------------------------------------------------------------------
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            "1. Z-Scores Non-Commercials (1Y vs 3Y)",
            "2. Z-Scores Commercials (1Y vs 3Y)",
            "3. Net Positioning Non-Commercials (Contratti)",
            "4. Net Positioning Commercials (Contratti)",
            "5. Z-Scores Open Interest (1Y vs 3Y)",
            "6. Open Interest Totale (Contratti Attivi)"
        ),
        vertical_spacing=0.10,
        horizontal_spacing=0.08
    )

    # Riga 1: Z-Scores Non-Comm e Comm
    fig.add_trace(go.Scatter(x=asset_data["Date"], y=asset_data["Non_Comm_Net_Z_1Y"], name="1Y Non-Comm Z", line=dict(color="#38bdf8", width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=asset_data["Date"], y=asset_data["Non_Comm_Net_Z_3Y"], name="3Y Non-Comm Z", line=dict(color="#f59e0b", width=1.5)), row=1, col=1)
    fig.add_hline(y=2.0, line_dash="dash", line_color="#ef4444", row=1, col=1)
    fig.add_hline(y=-2.0, line_dash="dash", line_color="#10b981", row=1, col=1)

    fig.add_trace(go.Scatter(x=asset_data["Date"], y=asset_data["Comm_Net_Z_1Y"], name="1Y Comm Z", line=dict(color="#38bdf8", width=1.5)), row=1, col=2)
    fig.add_trace(go.Scatter(x=asset_data["Date"], y=asset_data["Comm_Net_Z_3Y"], name="3Y Comm Z", line=dict(color="#f59e0b", width=1.5)), row=1, col=2)
    fig.add_hline(y=2.0, line_dash="dash", line_color="#ef4444", row=1, col=2)
    fig.add_hline(y=-2.0, line_dash="dash", line_color="#10b981", row=1, col=2)

    # Riga 2: Barre di Posizionamento Netto
    fig.add_trace(go.Bar(x=asset_data["Date"], y=asset_data["Non_Comm_Net"], name="Net Non-Comm", marker_color="#00D1FF"), row=2, col=1)
    fig.add_trace(go.Bar(x=asset_data["Date"], y=asset_data["Comm_Net"], name="Net Comm", marker_color="#FF6B6B"), row=2, col=2)

    # Riga 3: Open Interest Z-Score & Volume Contratti
    fig.add_trace(go.Scatter(x=asset_data["Date"], y=asset_data["Open_Interest_Z_1Y"], name="1Y OI Z", line=dict(color="#38bdf8", width=1.5)), row=3, col=1)
    fig.add_trace(go.Scatter(x=asset_data["Date"], y=asset_data["Open_Interest_Z_3Y"], name="3Y OI Z", line=dict(color="#f59e0b", width=1.5)), row=3, col=1)
    fig.add_trace(go.Bar(x=asset_data["Date"], y=asset_data["Open_Interest"], name="Open Interest", marker_color="#00CC96"), row=3, col=2)

    fig.update_layout(
        height=1000,
        template="plotly_dark",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)
