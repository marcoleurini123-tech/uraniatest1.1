import pandas as pd
from typing import Optional, Dict, Any
from core.data_engine import calculate_eod_poc

def evaluate_poc_capitulation(df: pd.DataFrame, min_drawdown: float = -30.0, max_poc_dist: float = 5.0) -> Optional[Dict[str, Any]]:
    """
    Protocollo 1: Caccia ai minimi (Bottom Hunter).
    Condizioni: Drawdown profondo dai massimi e prezzo compresso attorno al POC volumetrico.
    """
    if len(df) < 60:
        return None

    last_close = float(df['Close'].iloc[-1])
    ath_high = float(df['High'].max())
    drawdown = ((last_close / ath_high) - 1.0) * 100.0
    poc_price = calculate_eod_poc(df)
    poc_dist = ((last_close - poc_price) / poc_price) * 100.0

    if drawdown <= min_drawdown and abs(poc_dist) <= max_poc_dist:
        stop_loss = poc_price * 0.95
        target = poc_price * 1.25
        risk = last_close - stop_loss
        reward = target - last_close
        rr = reward / risk if risk > 0 else 0.0

        return {
            "name": "POC Capitulation (Bottom Hunter)",
            "price": last_close,
            "drawdown": drawdown,
            "poc": poc_price,
            "poc_dist": poc_dist,
            "target": target,
            "rr_ratio": rr
        }
    return None
