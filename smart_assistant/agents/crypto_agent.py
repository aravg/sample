from .base_agent import BaseAgent

API_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin,ethereum,dogecoin&vs_currencies=usd,inr"
)


class CryptoAgent(BaseAgent):
    def execute(self, query: str) -> dict:
        try:
            data = self.fetch_with_retry(API_URL)
            processed = {}
            for coin, prices in data.items():
                processed[coin.capitalize()] = {
                    "USD": f"${prices.get('usd', 'N/A'):,}",
                    "INR": f"₹{prices.get('inr', 'N/A'):,}",
                }
            return {
                "status": "success",
                "agent": "crypto",
                "raw_data": data,
                "processed": processed,
            }
        except Exception as e:
            return {"status": "error", "agent": "crypto", "error": str(e)}
