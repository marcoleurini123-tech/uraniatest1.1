import pandas as pd
import numpy as np

def evaluate_macro_visual_alerts(df: pd.DataFrame) -> list[dict]:
    """Valuta divergenze ed eccessi macroeconomici SOLO per visualizzazione a schermo."""
    if len(df) < 6:
        return []
    
    last = df.iloc[-1]
    prev5 = df.iloc[-6]
    alerts = []

    # 1. Divergenza Bearish: Liquidità Fed vs SPY
    if prev5.get('Net_Liquidity', 0) > 0:
        liq_delta = ((last['Net_Liquidity'] - prev5['Net_Liquidity']) / prev5['Net_Liquidity']) * 100.0
        if liq_delta < -1.0 and last.get('SPY', 0) > prev5.get('SPY', 0):
            alerts.append({
                "type": "Divergenza Liquidità Fed vs Mercato",
                "severity": "CRITICAL",
                "color": "#ef4444",
                "desc": f"Liquidità Netta in contrazione ({liq_delta:+.2f}% a 5gg) mentre lo SPY fa nuovi massimi relativi. Rischio elevato di bull-trap o storno per prosciugamento monetario."
            })

    # 2. Inversione Curva di Volatilità (VIX Backwardation)
    vix1d = last.get('VIX1D', 0)
    vix = last.get('VIX', 0)
    if vix1d > vix and vix > 0:
        alerts.append({
            "type": "Inversione Curva Volatilità (VIX1D > VIX)",
            "severity": "HIGH",
            "color": "#f59e0b",
            "desc": f"La struttura a termine della volatilità è invertita ({vix1d:.1f} vs {vix:.1f}). Forte domanda di coperture immediate / stress di brevissimo termine."
        })

    # 3. Tail Risk / Cigno Nero (SKEW Index ed Eccesso Stress)
    skew = last.get('SKEW', 0)
    move = last.get('MOVE', 0)
    if skew >= 140 or move >= 115:
        alerts.append({
            "type": "Eccesso Rischio Coda / Stress Obbligazionario",
            "severity": "WARNING",
            "color": "#d97706",
            "desc": f"SKEW Index a {skew:.1f} e MOVE Index a {move:.1f}. Elevato premio pagato dagli istituzionali per Puts Out-of-The-Money o turbolenza tassi."
        })

    # 4. Spreads di Credito Corporate (HYG vs LQD)
    if 'HYG' in df.columns and 'LQD' in df.columns:
        ratio_credit = df['HYG'] / df['LQD'].replace(0, np.nan)
        sma20_credit = ratio_credit.rolling(20).mean().iloc[-1]
        if ratio_credit.iloc[-1] < sma20_credit * 0.985:
            alerts.append({
                "type": "Deterioramento Spreads di Credito High Yield",
                "severity": "HIGH",
                "color": "#ef4444",
                "desc": f"Rapporto HYG/LQD sotto la media 20gg. Gli investitori istituzionali richiedono maggior premio al rischio sul debito societario."
            })

    # 5. Breadth Anomala (SPY vs RSP)
    if last.get('RSP', 0) > 0:
        ratio_br = last['SPY'] / last['RSP']
        if ratio_br >= 3.45:
            alerts.append({
                "type": "Anomalia di Ampiezza (Market Breadth)",
                "severity": "WARNING",
                "color": "#eab308",
                "desc": f"Rapporto SPY/RSP a {ratio_br:.2f}. Il mercato è concentrato su poche mega-cap: indice vulnerabile se mancano i flussi sulle medie/piccole."
            })

    return alerts
