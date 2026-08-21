import pandas as pd
from typing import Optional, Dict, Any
from core.data_engine import calculate_eod_poc

def evaluate_rounding_breakout(df: pd.DataFrame, lookback: int = 120) -> Optional[Dict[str, Any]]:
    """
    Protocollo 2: Base ad U + Rottura Neckline con supporto volumetrico.
    """
    if len(df) < lookback:
        return None

    data = df.tail(lookback)
    close = data['Close'].values
    last_close = float(close[-1])
    
    mid = len(close) // 2
    left_high = float(close[:mid // 2].max())
    bottom_min = float(close[mid - 20 : mid + 20].min())
    poc_price = calculate_eod_poc(data)
    
    u_depth = (left_high - bottom_min) / left_high
    breakout = last_close >= (left_high * 0.985)

    if u_depth >= 0.15 and breakout:
        stop_loss = poc_price * 0.95
        target = left_high * 1.30
        risk = last_close - stop_loss
        reward = target - last_close
        rr = reward / risk if risk > 0 else 0.0

        return {
            "name": "Rounding Base & Breakout",
            "price": last_close,
            "drawdown": ((last_close / df['High'].max()) - 1.0) * 100.0,
            "poc": poc_price,
            "poc_dist": ((last_close - poc_price) / poc_price) * 100.0,
            "target": target,
            "rr_ratio": rr
        }
    return None
