import json
import os
from openai import OpenAI

SYSTEM_PROMPT = """You are a routing agent for a Smart Personal Assistant. Analyze the user query and decide which specialized agents should handle it.

Available agents:
- weather   : weather, temperature, rain, forecast, humidity, wind
- crypto    : cryptocurrency prices — Bitcoin, Ethereum, Dogecoin, BTC, ETH, DOGE
- currency  : currency exchange rates, USD to INR, forex conversion
- joke      : jokes, humor, funny content, laugh
- quote     : motivational quotes, inspiration, wisdom, affirmations

Rules:
1. Return ONLY a valid JSON object: {"agents": ["agent1", "agent2"]}
2. Select ALL agents that match the query — multiple agents are fine.
3. If no agent matches, return {"agents": []} and the assistant will respond generically.

Examples:
  "What's the weather?" -> {"agents": ["weather"]}
  "Bitcoin price and weather?" -> {"agents": ["weather", "crypto"]}
  "Tell me a joke and inspire me" -> {"agents": ["joke", "quote"]}
  "Convert USD to INR" -> {"agents": ["currency"]}
  "Show me everything" -> {"agents": ["weather", "crypto", "currency", "joke", "quote"]}
"""


class RouterAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def route(self, query: str) -> list[str]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        result = json.loads(response.choices[0].message.content)
        agents = result.get("agents", [])
        valid = {"weather", "crypto", "currency", "joke", "quote"}
        return [a for a in agents if a in valid]
