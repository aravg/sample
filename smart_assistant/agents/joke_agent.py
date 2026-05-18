from .base_agent import BaseAgent

API_URL = "https://v2.jokeapi.dev/joke/Any?safe-mode"


class JokeAgent(BaseAgent):
    def execute(self, query: str) -> dict:
        try:
            data = self.fetch_with_retry(API_URL)
            if data.get("type") == "single":
                joke_text = data.get("joke", "")
            else:
                setup = data.get("setup", "")
                delivery = data.get("delivery", "")
                joke_text = f"{setup}\n— {delivery}"
            return {
                "status": "success",
                "agent": "joke",
                "raw_data": data,
                "processed": {
                    "category": data.get("category", "Any"),
                    "type": data.get("type"),
                    "joke": joke_text,
                },
            }
        except Exception as e:
            return {"status": "error", "agent": "joke", "error": str(e)}
