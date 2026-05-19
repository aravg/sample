# AI Trip Planner — Multi-Agent LangGraph System

A production-grade Agentic AI system built with **LangGraph** where 11 specialized agents collaborate under an **Orchestrator Agent** to generate complete personalized trip plans with a downloadable PDF report.

## Architecture

```
START
  └─► Orchestrator Agent (Supervisor)
        ├─► User Input Agent        — Collect & validate requirements
        ├─► Memory Agent             — Retrieve past preferences (FAISS + SQLite)
        ├─► Gather Data [Parallel]
        │     ├─► Weather Agent      — OpenWeatherMap API
        │     ├─► Transport Agent    — Flights / Trains / Routes
        │     ├─► Hotel Agent        — Hotels within budget
        │     └─► Places Agent       — Attractions & experiences
        ├─► Budget Agent             — Cost optimization
        ├─► Itinerary Agent          — Day-wise plan (LLM-generated)
        ├─► Final Review Agent       — Validation + conflict resolution
        │     └─► Retry if needed ──► Agents above
        ├─► Memory Update Agent      — Save to memory
        └─► PDF Generator Agent      — Professional travel report
              └─► END
```

## Tech Stack

| Component       | Technology                       |
|-----------------|----------------------------------|
| Workflow Engine | LangGraph                        |
| LLM             | Claude (Anthropic) / GPT-4       |
| Memory          | FAISS + SQLite                   |
| PDF             | ReportLab                        |
| UI              | Streamlit                        |
| Weather API     | OpenWeatherMap                   |
| Web Search      | DuckDuckGo (no key needed)       |

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
copy .env.example .env
```
Edit `.env` and add your API keys:
```
ANTHROPIC_API_KEY=your_key_here
OPENWEATHERMAP_API_KEY=your_key_here   # free at openweathermap.org
```

### 3. Run

**Streamlit UI (recommended):**
```bash
streamlit run app.py
```

**CLI:**
```bash
python main.py "Plan a 5-day Goa trip from Bangalore for a couple, budget Rs.30000"
```

## Project Structure

```
trip_planner/
├── app.py                    # Streamlit UI
├── main.py                   # CLI entry point
├── workflow.py               # LangGraph StateGraph definition
├── state.py                  # TripState schema
├── config.py                 # Configuration & LLM factory
├── agents/
│   ├── orchestrator.py       # Supervisor — routes all agents
│   ├── user_input_agent.py   # Validates user requirements
│   ├── memory_agent.py       # Reads/writes memory stores
│   ├── weather_agent.py      # OpenWeatherMap integration
│   ├── transport_agent.py    # Flights, trains, routes
│   ├── hotel_agent.py        # Hotel recommendations
│   ├── places_agent.py       # Attractions & experiences
│   ├── budget_agent.py       # Cost calculation & optimization
│   ├── itinerary_agent.py    # Day-wise plan (LLM)
│   ├── review_agent.py       # Validation & conflict detection
│   └── pdf_generator_agent.py
├── tools/
│   ├── weather_tools.py
│   ├── transport_tools.py
│   ├── hotel_tools.py
│   ├── places_tools.py
│   ├── budget_tools.py
│   └── search_tools.py       # DuckDuckGo web search
├── memory/
│   ├── vector_store.py       # FAISS-based semantic memory
│   └── session_store.py      # SQLite trip history
├── utils/
│   └── pdf_generator.py      # ReportLab PDF with 6 sections
├── data/                     # Auto-created: DB + vector store
└── output/                   # Auto-created: PDF reports
```

## PDF Report Sections

1. **Cover Page** — Trip summary
2. **Section 1** — Flights & Transport
3. **Section 2** — Hotel Recommendations
4. **Section 3** — Day-wise Itinerary
5. **Section 4** — Budget Report
6. **Section 5** — Packing Checklist
7. **Section 6** — Emergency Contacts

## Sample Query

```
Plan a 5-day Goa trip from Bangalore for a couple.
Budget: ₹30,000
Need: beach resort, nightlife, sightseeing, seafood, flight preferred
```

## Orchestrator Logic

The Orchestrator Agent uses an LLM to decide routing at each step:
- **Conflict resolution**: If hotel exceeds budget → retry Hotel Agent with lower budget
- **Weather adaptation**: If rain forecast → adjust Places Agent recommendations  
- **Retry logic**: Up to 3 retries per agent before auto-approval
- **Final approval**: Validates completeness before triggering PDF generation
