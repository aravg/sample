"""Streamlit UI for the AI Trip Planner Multi-Agent System."""
import os
import sys
import json
import time
import threading
from datetime import datetime, date, timedelta
import streamlit as st
from langchain_core.messages import HumanMessage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from state import initial_state
from workflow import get_workflow

st.set_page_config(
    page_title="AI Trip Planner",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)

BRAND_CSS = """
<style>
    .main-header {
        background: linear-gradient(135deg, #1E5F74, #133B5C);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: #f0f8ff;
        border-left: 4px solid #1E5F74;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        margin: 0.4rem 0;
        font-size: 0.9rem;
    }
    .agent-card.active {
        background: #fff3cd;
        border-left-color: #FFA62B;
    }
    .agent-card.done {
        background: #d4edda;
        border-left-color: #28a745;
    }
    .metric-card {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .section-header {
        background: #1E5F74;
        color: white;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        margin: 1rem 0 0.5rem 0;
        font-weight: bold;
    }
    .day-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1E5F74, #133B5C);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-size: 1rem;
        font-weight: bold;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #FFA62B, #ff8c00);
        transform: translateY(-1px);
    }
</style>
"""
st.markdown(BRAND_CSS, unsafe_allow_html=True)

AGENTS = [
    ("orchestrator", "Orchestrator Agent", "Brain of the system"),
    ("user_input", "User Input Agent", "Collecting & validating requirements"),
    ("memory_retrieval", "Memory Agent", "Retrieving past preferences"),
    ("gather_data", "Data Gathering Agents", "Weather + Hotel + Transport + Places"),
    ("budget", "Budget Agent", "Calculating & optimizing costs"),
    ("itinerary", "Itinerary Agent", "Generating day-wise plan"),
    ("review", "Review Agent", "Validating & checking conflicts"),
    ("memory_update", "Memory Update Agent", "Saving to memory"),
    ("pdf_generator", "PDF Generator Agent", "Creating your travel report"),
]


def render_header():
    st.markdown("""
    <div class="main-header">
        <h1>✈ AI Trip Planner</h1>
        <p>Multi-Agent LangGraph System | Orchestrated by AI | Powered by Claude</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("## 🤖 Agent Status")
        completed = st.session_state.get("completed_agents", set())
        active = st.session_state.get("active_agent", "")

        for agent_id, agent_name, agent_desc in AGENTS:
            if agent_id in completed:
                css = "done"
                icon = "✅"
            elif agent_id == active:
                css = "active"
                icon = "⏳"
            else:
                css = ""
                icon = "⬜"
            st.markdown(
                f'<div class="agent-card {css}">{icon} <b>{agent_name}</b><br><small>{agent_desc}</small></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown("### System Info")
        st.markdown("**Architecture:** LangGraph Multi-Agent")
        st.markdown("**Memory:** FAISS + SQLite")
        st.markdown("**PDF:** ReportLab")


def render_input_form():
    st.markdown("### 📋 Plan Your Trip")

    col1, col2 = st.columns(2)
    with col1:
        source = st.text_input("From (Source City)", value="Bangalore", placeholder="e.g., Mumbai")
        destination = st.text_input("To (Destination)", value="Goa", placeholder="e.g., Goa")
        days = st.slider("Duration (Days)", 2, 14, 5)
        travel_type = st.selectbox("Travel Type", ["couple", "solo", "family", "business"])

    with col2:
        travelers = st.number_input("Number of Travelers", 1, 20, 2)
        budget = st.number_input("Total Budget (₹)", 5000, 500000, 30000, step=1000)
        hotel_pref = st.selectbox("Hotel Preference", ["mid-range", "budget", "luxury"])
        transport_pref = st.selectbox("Transport Preference", ["flight", "train", "bus", "car"])

    col3, col4 = st.columns(2)
    with col3:
        food_prefs = st.multiselect(
            "Food Preferences",
            ["seafood", "vegetarian", "street food", "fine dining", "local cuisine", "continental"],
            default=["seafood", "local cuisine"],
        )
    with col4:
        interests = st.multiselect(
            "Interests",
            ["beach", "nightlife", "heritage", "adventure", "nature", "culture", "shopping", "food"],
            default=["beach", "nightlife"],
        )

    user_name = st.text_input("Your Name", value="Traveler")

    start_date = date.today() + timedelta(days=30)
    end_date = start_date + timedelta(days=days)

    query = (
        f"Plan a {days}-day trip to {destination} from {source} for "
        f"{travelers} {travel_type} traveler(s). "
        f"Total budget: ₹{budget:,}. "
        f"Hotel: {hotel_pref}. Transport: {transport_pref} preferred. "
        f"Food preferences: {', '.join(food_prefs)}. "
        f"Interested in: {', '.join(interests)}. "
        f"Travel dates: {start_date} to {end_date}."
    )

    st.markdown(f"**Generated Query:** _{query}_")

    return {
        "query": query,
        "user_name": user_name,
        "source": source,
        "destination": destination,
        "days": days,
        "travelers": travelers,
        "budget": budget,
        "travel_type": travel_type,
        "hotel_preference": hotel_pref,
        "transport_preference": transport_pref,
        "food_preferences": food_prefs,
        "interests": interests,
        "dates": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "display": f"{start_date} to {end_date}",
        },
    }


def run_workflow_streaming(form_data: dict):
    """Execute the multi-agent workflow and stream progress to Streamlit."""
    state = initial_state()
    state["messages"] = [HumanMessage(content=form_data["query"])]
    state["user_profile"] = {
        "name": form_data["user_name"],
        "user_id": form_data["user_name"].lower().replace(" ", "_"),
        "email": f"{form_data['user_name'].lower()}@example.com",
    }
    state["trip_preferences"] = {
        "source": form_data["source"],
        "destination": form_data["destination"],
        "days": form_data["days"],
        "travelers": form_data["travelers"],
        "budget": form_data["budget"],
        "travel_type": form_data["travel_type"],
        "hotel_preference": form_data["hotel_preference"],
        "transport_preference": form_data["transport_preference"],
        "food_preferences": form_data["food_preferences"],
        "interests": form_data["interests"],
        "dates": form_data["dates"],
        "luxury_level": form_data["hotel_preference"],
    }

    if "completed_agents" not in st.session_state:
        st.session_state.completed_agents = set()
    if "active_agent" not in st.session_state:
        st.session_state.active_agent = ""

    progress_bar = st.progress(0, text="Starting AI Agents...")
    status_box = st.empty()
    log_expander = st.expander("Agent Execution Log", expanded=False)
    log_messages = []

    workflow = get_workflow()
    final_state = state
    step = 0
    total_steps = 9

    try:
        for event in workflow.stream(state, {"recursion_limit": 25}):
            for node_name, node_state in event.items():
                if node_name == "__end__":
                    continue

                step += 1
                st.session_state.active_agent = node_name
                progress = min(step / total_steps, 0.95)
                progress_bar.progress(progress, text=f"Running: {node_name.replace('_', ' ').title()}...")

                decision = node_state.get("orchestrator_decision", {})
                log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] {node_name}: {decision.get('reason', 'Processing...')}"
                log_messages.append(log_msg)
                with log_expander:
                    st.text("\n".join(log_messages[-10:]))

                agent_map = {
                    "user_input": "user_input",
                    "memory_retrieval": "memory_retrieval",
                    "gather_data": "gather_data",
                    "budget": "budget",
                    "itinerary": "itinerary",
                    "review": "review",
                    "memory_update": "memory_update",
                    "pdf_generator": "pdf_generator",
                    "orchestrator": "orchestrator",
                }
                if node_name in agent_map:
                    st.session_state.completed_agents.add(agent_map[node_name])

                status_box.info(f"**{node_name.replace('_', ' ').title()}** → {decision.get('next_step', '...')}")
                final_state = node_state

                if node_state.get("pdf_status", {}).get("generated"):
                    progress_bar.progress(1.0, text="Complete!")
                    status_box.success("Trip plan generated successfully!")
                    return final_state

    except Exception as e:
        st.error(f"Workflow error: {e}")
        progress_bar.progress(1.0)
        return final_state

    progress_bar.progress(1.0, text="Done!")
    return final_state


def render_results(final_state: dict):
    prefs = final_state.get("trip_preferences", {})
    budget_summary = final_state.get("budget_summary", {})
    itinerary = final_state.get("itinerary", {})
    weather = final_state.get("weather_data", {})
    hotel = final_state.get("hotel_data", {})
    transport = final_state.get("transport_data", {})
    places = final_state.get("places_data", {})
    review = final_state.get("review_status", {})
    pdf_path = final_state.get("pdf_path")

    st.markdown("---")
    st.markdown("## 🎉 Your Trip Plan is Ready!")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Destination", prefs.get("destination", "N/A"))
    with col2:
        st.metric("Duration", f"{prefs.get('days', 0)} days")
    with col3:
        total = budget_summary.get("total_inr", 0)
        allocated = prefs.get("budget", 0)
        delta = allocated - total
        st.metric("Estimated Cost", f"₹{total:,.0f}", delta=f"₹{delta:,.0f} {'saved' if delta >= 0 else 'over'}")
    with col4:
        score = review.get("confidence_score", 0)
        st.metric("Plan Score", f"{score}/100")

    tabs = st.tabs(["🗓 Itinerary", "🏨 Hotel", "✈ Transport", "🌤 Weather", "📍 Places", "💰 Budget", "📄 PDF"])

    with tabs[0]:
        st.markdown('<div class="section-header">Day-wise Itinerary</div>', unsafe_allow_html=True)
        days_data = itinerary.get("days", [])
        if days_data:
            for day in days_data:
                with st.expander(f"**Day {day['day']}: {day.get('title', '')}**", expanded=day["day"] <= 2):
                    acts = day.get("activities", [])
                    for act in acts:
                        cost_str = f" — ₹{act['cost']}" if act.get("cost") else ""
                        st.markdown(f"**{act.get('time', '')}**: {act.get('description', '')}{cost_str}")
                    if food := day.get("food"):
                        st.markdown(f"🍽 **Food**: {food}")
                    if hotel_name := day.get("accommodation"):
                        st.markdown(f"🏨 **Stay**: {hotel_name}")
        if tips := itinerary.get("tips"):
            st.markdown("**Travel Tips:**")
            for tip in tips:
                st.markdown(f"- {tip}")

    with tabs[1]:
        st.markdown('<div class="section-header">Hotel Recommendations</div>', unsafe_allow_html=True)
        recs = hotel.get("recommendations", [])
        if recs:
            for h in recs:
                is_best = hotel.get("best_pick", {}).get("name") == h["name"]
                with st.expander(f"{'⭐ TOP PICK: ' if is_best else ''}{h['name']} ({'★' * h.get('stars', 0)})", expanded=is_best):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Per Night", f"₹{h.get('price_per_night', 0):,.0f}")
                        st.metric("Total Stay", f"₹{h.get('total_cost_inr', 0):,.0f}")
                    with col_b:
                        st.metric("Rating", f"{h.get('rating', 0)}/5")
                        st.markdown(f"**Area:** {h.get('area', 'N/A')}")
                    if amenities := h.get("amenities"):
                        st.markdown(f"**Amenities:** {', '.join(amenities)}")

    with tabs[2]:
        st.markdown('<div class="section-header">Transport Options</div>', unsafe_allow_html=True)
        if flights_data := transport.get("flights"):
            st.markdown("**Outbound Flights:**")
            flights = flights_data.get("flights", [])
            if flights:
                cols = st.columns(len(flights[:3]))
                for i, f in enumerate(flights[:3]):
                    with cols[i]:
                        st.markdown(f"**{f['airline']}**")
                        st.markdown(f"Duration: {f['duration']}")
                        st.markdown(f"Price: ₹{f.get('total_price_inr', 0):,.0f}")

        if trains_data := transport.get("trains"):
            trains = trains_data.get("trains", [])
            if trains:
                st.markdown("**Train Options:**")
                for t in trains:
                    st.markdown(f"- **{t['name']}** ({t['number']}): {t['duration']} — ₹{t.get('total_price_inr', 0):,.0f}")

        if rec := transport.get("recommendation"):
            st.info(f"**Recommendation:** {rec}")

    with tabs[3]:
        st.markdown('<div class="section-header">Weather Forecast</div>', unsafe_allow_html=True)
        if summary := weather.get("summary"):
            st.info(summary)
        forecasts = weather.get("forecasts", [])
        if forecasts:
            cols = st.columns(min(len(forecasts), 5))
            for i, f in enumerate(forecasts[:5]):
                with cols[i]:
                    st.metric(
                        label=f.get("date", "")[-5:],
                        value=f"{f.get('temp_max', 0):.0f}°C",
                        delta=f"min {f.get('temp_min', 0):.0f}°C",
                    )
                    st.caption(f.get("description", ""))

    with tabs[4]:
        st.markdown('<div class="section-header">Must-Visit Places</div>', unsafe_allow_html=True)
        attractions = places.get("attractions", [])
        if attractions:
            for att in attractions[:8]:
                fee = att.get("entry_fee", 0)
                fee_str = f"₹{fee}" if fee else "Free"
                st.markdown(f"**{att['name']}** ({att.get('type', '').capitalize()}) — Entry: {fee_str}")
                st.caption(att.get("description", ""))

        if experiences := places.get("local_experiences"):
            st.markdown("**Local Experiences:**")
            for exp in experiences:
                st.markdown(f"- {exp}")

    with tabs[5]:
        st.markdown('<div class="section-header">Budget Report</div>', unsafe_allow_html=True)
        breakdown = budget_summary.get("breakdown", {})
        if breakdown:
            total = budget_summary.get("total_inr", 0)
            allocated = prefs.get("budget", 0)
            cols = st.columns(len(breakdown))
            for i, (k, v) in enumerate(breakdown.items()):
                with cols[i]:
                    pct = (v / total * 100) if total else 0
                    st.metric(k.replace("_", " ").title(), f"₹{v:,.0f}", delta=f"{pct:.1f}%")

            st.markdown("---")
            col_l, col_r = st.columns(2)
            with col_l:
                st.metric("Total Estimated", f"₹{total:,.0f}")
                st.metric("Budget Allocated", f"₹{allocated:,.0f}")
            with col_r:
                st.metric("Per Person", f"₹{budget_summary.get('per_person_inr', 0):,.0f}")
                st.metric("Daily Average", f"₹{budget_summary.get('daily_avg_inr', 0):,.0f}")

        if suggestions := budget_summary.get("suggestions"):
            st.markdown("**Cost-saving Tips:**")
            for s in suggestions:
                st.markdown(f"- {s}")

    with tabs[6]:
        st.markdown('<div class="section-header">Download Your Travel Report</div>', unsafe_allow_html=True)
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            dest = prefs.get("destination", "Trip")
            st.success(f"✅ PDF report ready: `{os.path.basename(pdf_path)}`")
            st.download_button(
                label="⬇ Download PDF Travel Report",
                data=pdf_bytes,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
                use_container_width=True,
            )
            st.markdown(f"**File size:** {len(pdf_bytes):,} bytes")
        else:
            st.warning("PDF generation in progress or encountered an error.")
            errors = final_state.get("errors", [])
            if errors:
                st.error("\n".join(errors))


def main():
    render_header()
    render_sidebar()

    if "result" not in st.session_state:
        st.session_state.result = None
    if "running" not in st.session_state:
        st.session_state.running = False

    form_data = render_input_form()

    st.markdown("---")
    if st.button("🚀 Generate My Trip Plan", use_container_width=True):
        st.session_state.completed_agents = set()
        st.session_state.active_agent = "orchestrator"
        st.session_state.running = True

        with st.spinner("AI agents are planning your trip..."):
            result = run_workflow_streaming(form_data)
            st.session_state.result = result
            st.session_state.running = False

    if st.session_state.result and not st.session_state.running:
        render_results(st.session_state.result)


if __name__ == "__main__":
    main()
