import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
APP_TITLE = os.getenv("APP_TITLE", "AI Trip Planner")

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "trips.db")
VECTOR_STORE_PATH = os.path.join(os.path.dirname(__file__), "data", "vector_store")
PDF_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)


def get_llm(temperature: float = 0.7):
    if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=LLM_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=temperature,
        )
    elif ANTHROPIC_API_KEY:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=ANTHROPIC_API_KEY,
            temperature=temperature,
            max_tokens=4096,
        )
    else:
        raise ValueError(
            "No valid LLM API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env"
        )
