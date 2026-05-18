from .base_agent import BaseAgent

PRIMARY_URL = "https://api.quotable.io/random"
FALLBACK_URL = "https://zenquotes.io/api/random"


class QuoteAgent(BaseAgent):
    def execute(self, query: str) -> dict:
        try:
            return self._fetch_quotable()
        except Exception:
            try:
                return self._fetch_zenquotes()
            except Exception as e:
                return {"status": "error", "agent": "quote", "error": str(e)}

    def _fetch_quotable(self) -> dict:
        data = self.fetch_with_retry(PRIMARY_URL)
        return {
            "status": "success",
            "agent": "quote",
            "raw_data": data,
            "processed": {
                "quote": data.get("content", ""),
                "author": data.get("author", "Unknown"),
                "tags": data.get("tags", []),
                "source": "quotable.io",
            },
        }

    def _fetch_zenquotes(self) -> dict:
        data = self.fetch_with_retry(FALLBACK_URL)
        entry = data[0] if isinstance(data, list) and data else {}
        return {
            "status": "success",
            "agent": "quote",
            "raw_data": data,
            "processed": {
                "quote": entry.get("q", ""),
                "author": entry.get("a", "Unknown"),
                "tags": [],
                "source": "zenquotes.io",
            },
        }
