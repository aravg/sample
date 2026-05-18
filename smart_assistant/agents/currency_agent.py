from .base_agent import BaseAgent

API_URL = "https://open.er-api.com/v6/latest/USD"

HIGHLIGHT_CURRENCIES = ["INR", "EUR", "GBP", "JPY", "AUD", "CAD", "SGD", "AED"]


class CurrencyAgent(BaseAgent):
    def execute(self, query: str) -> dict:
        try:
            data = self.fetch_with_retry(API_URL)
            rates = data.get("rates", {})
            highlighted = {c: rates[c] for c in HIGHLIGHT_CURRENCIES if c in rates}
            return {
                "status": "success",
                "agent": "currency",
                "raw_data": data,
                "processed": {
                    "base": "USD",
                    "last_updated": data.get("time_last_update_utc", "N/A"),
                    "key_rates": highlighted,
                    "total_currencies": len(rates),
                },
            }
        except Exception as e:
            return {"status": "error", "agent": "currency", "error": str(e)}
