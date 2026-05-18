import os
import sys
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not set. Copy .env.example to .env and add your key.")
    sys.exit(1)

from agents import RouterAgent, WeatherAgent, CryptoAgent, CurrencyAgent, JokeAgent, QuoteAgent, CombinerAgent
from report_generator import ReportGenerator

AGENT_MAP = {
    "weather": WeatherAgent(),
    "crypto": CryptoAgent(),
    "currency": CurrencyAgent(),
    "joke": JokeAgent(),
    "quote": QuoteAgent(),
}

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║          SMART PERSONAL ASSISTANT — Multi-Agent System       ║
╠══════════════════════════════════════════════════════════════╣
║  Agents: Weather | Crypto | Currency | Joke | Quote          ║
║  Type 'quit' or 'exit' to stop                               ║
╚══════════════════════════════════════════════════════════════╝
"""

WORKFLOW = """
  [User Query]
       │
       ▼
  ┌─────────────┐
  │ Router Agent│  ← identifies intent via OpenAI
  └──────┬──────┘
         │  activates one or more of:
    ┌────┴──────────────────────────────────────────┐
    │         │          │         │         │       │
    ▼         ▼          ▼         ▼         ▼
[Weather] [Crypto] [Currency] [Joke]   [Quote]
    │         │          │         │         │
    └─────────┴──────────┴─────────┴─────────┘
                         │
                         ▼
                ┌────────────────┐
                │ Combiner Agent │  ← merges via OpenAI
                └───────┬────────┘
                        │
              ┌─────────┴──────────┐
              ▼                    ▼
      [Final Response]    [Report .txt + .json]
"""


def print_workflow():
    print(WORKFLOW)


def run():
    router = RouterAgent()
    combiner = CombinerAgent()
    reporter = ReportGenerator()

    print(BANNER)
    print_workflow()

    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if query.lower() == "workflow":
            print_workflow()
            continue

        print("\n[Router Agent] Analyzing intent...")
        selected_agents = router.route(query)

        if selected_agents:
            print(f"[Router Agent] Activating: {', '.join(a.capitalize() for a in selected_agents)}")
        else:
            print("[Router Agent] No specific agent matched — using general response.")

        agent_results = {}
        for agent_name in selected_agents:
            agent = AGENT_MAP.get(agent_name)
            if agent:
                print(f"[{agent_name.capitalize()} Agent] Fetching data from API...")
                result = agent.execute(query)
                agent_results[agent_name] = result
                status = result.get("status", "unknown")
                icon = "OK" if status == "success" else "FAILED"
                print(f"[{agent_name.capitalize()} Agent] {icon}")

        print("[Combiner Agent] Synthesizing response...")
        final_response = combiner.combine(query, agent_results)

        print(f"\nAssistant:\n{final_response}\n")

        report_path = reporter.generate(query, selected_agents, agent_results, final_response)
        print(f"[Report] Saved → {report_path}")
        print("-" * 66 + "\n")


if __name__ == "__main__":
    run()
