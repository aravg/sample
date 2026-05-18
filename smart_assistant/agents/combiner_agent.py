import json
import os
from openai import OpenAI

SYSTEM_PROMPT = """You are a Combiner Agent for a Smart Personal Assistant.
Your job is to synthesize responses from multiple specialized agents into one clear, friendly, and informative reply.

Rules:
- Write a natural, conversational response — not a list of raw data dumps.
- Remove redundant information.
- Format numbers clearly (e.g., "$104,000" not "104000").
- If an agent failed, mention it briefly but focus on what succeeded.
- Keep the response concise but complete.
- Do NOT mention "agents" or technical internals — just answer the user directly.
"""


class CombinerAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def combine(self, query: str, agent_results: dict) -> str:
        if not agent_results:
            return self._general_response(query)

        data_summary = json.dumps(
            {name: res.get("processed", res.get("error", "failed"))
             for name, res in agent_results.items()},
            indent=2,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"User asked: \"{query}\"\n\n"
                        f"Data collected from agents:\n{data_summary}\n\n"
                        "Please write a clear, friendly response."
                    ),
                },
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    def _general_response(self, query: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful Smart Personal Assistant. "
                        "Answer the user's question directly and concisely."
                    ),
                },
                {"role": "user", "content": query},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
