import requests
from typing import Tuple, Dict, Any

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.token = token.strip()
        self.chat_id = chat_id.strip()
        self.url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def dispatch_alert(self, ticker: str, protocol_name: str, metrics: Dict[str, Any]) -> Tuple[bool, str]:
        message = (
            f"🚨 <b>URANIA RADAR — SEGNALE OPERATIVO</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 <b>Asset:</b> <code>${ticker}</code>\n"
            f"📈 <b>Protocollo:</b> {protocol_name}\n"
            f"💵 <b>Prezzo Ultimo EOD:</b> ${metrics.get('price', 0.0):.2f}\n"
            f"📉 <b>Drawdown da ATH:</b> {metrics.get('drawdown', 0.0):.1f}%\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📐 <b>LIVELLI STATISTICI & VOLUMETRICI:</b>\n"
            f"• <b>POC Volume Base:</b> ${metrics.get('poc', 0.0):.2f}\n"
            f"• <b>Distanza dal POC:</b> {metrics.get('poc_dist', 0.0):+.2f}%\n"
            f"• <b>Trigger Level:</b> ${metrics.get('trigger_price', 0.0):.2f}\n"
            f"• <b>Target Superiore:</b> ${metrics.get('target', 0.0):.2f}\n"
            f"• <b>Risk / Reward:</b> {metrics.get('rr_ratio', 0.0):.2f} : 1\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"ℹ️ <i>Analisi validata su dati storici EOD.</i>"
        )
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            r = requests.post(self.url, json=payload, timeout=10)
            res = r.json()
            if r.status_code == 200 and res.get("ok"):
                return True, "Segnale inoltrato con successo al canale Telegram."
            return False, f"Errore API Telegram: {res.get('description', 'Non autorizzato')}"
        except Exception as e:
            return False, f"Errore di connessione: {str(e)}"
