import requests
from typing import Tuple, Dict, Any

class TelegramDispatcher:
    def __init__(self, token: str, chat_id: str):
        self.token = token.strip()
        self.chat_id = chat_id.strip()
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_alert(self, ticker: str, setup_name: str, metrics: Dict[str, Any]) -> Tuple[bool, str]:
        message = (
            f"🚨 <b>URANIA RADAR — SEGNALE OPERATIVO</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 <b>Asset:</b> <code>${ticker}</code>\n"
            f"📈 <b>Protocollo:</b> {setup_name}\n"
            f"💵 <b>Prezzo Ultimo EOD:</b> ${metrics.get('price', 0.0):.2f}\n"
            f"📉 <b>Drawdown da Max:</b> {metrics.get('drawdown', 0.0):.1f}%\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📐 <b>LIVELLI STATISTICI & VOLUMETRICI:</b>\n"
            f"• <b>POC di Supporto:</b> ${metrics.get('poc', 0.0):.2f}\n"
            f"• <b>Distanza dal POC:</b> {metrics.get('poc_distance', 0.0):+.2f}%\n"
            f"• <b>Trigger Operativo:</b> {metrics.get('trigger_desc', 'Confermato')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"ℹ️ <i>Segnale generato dalla pipeline EOD di Urania System.</i>"
        )
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            r = requests.post(self.base_url, json=payload, timeout=10)
            data = r.json()
            if r.status_code == 200 and data.get("ok"):
                return True, "Alert inviato con successo al canale Telegram."
            return False, f"Errore Telegram: {data.get('description', 'Unauthorized')}"
        except Exception as e:
            return False, f"Errore Connessione: {str(e)}"
