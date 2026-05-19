"""
Test the full workflow with a mock LLM (no API key needed).
Patches the orchestrator and LLM calls with deterministic responses.
"""
import sys
import json
from unittest.mock import patch, MagicMock
sys.path.insert(0, '.')

from langchain_core.messages import HumanMessage, AIMessage
from state import initial_state

MOCK_ORCHESTRATOR_RESPONSES = [
    '{"next_step": "user_input", "reason": "Start with user input", "conflicts": []}',
    '{"next_step": "memory_retrieval", "reason": "Check memory", "conflicts": []}',
    '{"next_step": "gather_data", "reason": "Gather trip data", "conflicts": []}',
    '{"next_step": "budget", "reason": "Calculate budget", "conflicts": []}',
    '{"next_step": "itinerary", "reason": "Generate itinerary", "conflicts": []}',
    '{"next_step": "review", "reason": "Review plan", "conflicts": []}',
    '{"next_step": "pdf_generator", "reason": "Generate PDF", "conflicts": []}',
    '{"next_step": "end", "reason": "Done", "conflicts": []}',
]

MOCK_USER_INPUT = json.dumps({
    "source": "Bangalore",
    "destination": "Goa",
    "days": 5,
    "travelers": 2,
    "budget": 30000,
    "travel_type": "couple",
    "hotel_preference": "mid-range",
    "food_preferences": ["seafood"],
    "transport_preference": "flight",
    "interests": ["beach", "nightlife"],
    "luxury_level": "mid-range",
    "dates": {"start": "2026-06-20", "end": "2026-06-25", "display": "June 20-25, 2026"},
})

MOCK_ITINERARY = json.dumps({
    "days": [
        {"day": 1, "title": "Arrival",
         "activities": [{"time": "Morning", "description": "Arrive in Goa", "cost": 0}],
         "food": "Seafood dinner", "accommodation": "La Calypso Hotel"},
        {"day": 2, "title": "Beaches",
         "activities": [{"time": "Morning", "description": "Baga Beach", "cost": 0}],
         "food": "Beach shack lunch", "accommodation": "La Calypso Hotel"},
        {"day": 3, "title": "Heritage",
         "activities": [{"time": "Morning", "description": "Fort Aguada", "cost": 30}],
         "food": "Local cuisine", "accommodation": "La Calypso Hotel"},
        {"day": 4, "title": "Activities",
         "activities": [{"time": "Morning", "description": "Water sports", "cost": 1500}],
         "food": "Seafood dinner", "accommodation": "La Calypso Hotel"},
        {"day": 5, "title": "Departure",
         "activities": [{"time": "Morning", "description": "Shopping and departure", "cost": 0}],
         "food": "Breakfast at hotel", "accommodation": ""},
    ],
    "tips": ["Carry sunscreen", "Try local Feni"],
    "highlights": ["Baga Beach", "Fort Aguada"],
})

MOCK_REVIEW = json.dumps({
    "approved": True,
    "issues": [],
    "conflicts": [],
    "retry_agent": None,
    "review_notes": "Plan looks great!",
    "confidence_score": 92,
})

call_count = [0]

def mock_llm_invoke(messages):
    resp_map = {
        0: MOCK_ORCHESTRATOR_RESPONSES[0],
        1: MOCK_USER_INPUT,
        2: MOCK_ORCHESTRATOR_RESPONSES[1],
        3: MOCK_ORCHESTRATOR_RESPONSES[2],
        4: MOCK_ORCHESTRATOR_RESPONSES[3],
        5: MOCK_ITINERARY,
        6: MOCK_ORCHESTRATOR_RESPONSES[4],
        7: MOCK_REVIEW,
        8: MOCK_ORCHESTRATOR_RESPONSES[5],
        9: MOCK_ORCHESTRATOR_RESPONSES[6],
        10: MOCK_ORCHESTRATOR_RESPONSES[7],
    }
    idx = call_count[0] % len(MOCK_ORCHESTRATOR_RESPONSES)

    sys_content = str(messages[0].content) if messages else ""
    if "Orchestrator Agent" in sys_content:
        n = call_count[0]
        resp = MOCK_ORCHESTRATOR_RESPONSES[min(n, len(MOCK_ORCHESTRATOR_RESPONSES)-1)]
    elif "User Input Agent" in sys_content:
        resp = MOCK_USER_INPUT
    elif "expert travel planner" in sys_content:
        resp = MOCK_ITINERARY
    elif "Final Review Agent" in sys_content:
        resp = MOCK_REVIEW
    else:
        resp = MOCK_ORCHESTRATOR_RESPONSES[-1]

    call_count[0] += 1
    mock_resp = MagicMock()
    mock_resp.content = resp
    return mock_resp


def test_full_workflow():
    print("Testing full LangGraph workflow with mock LLM...")

    with patch('config.get_llm') as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke = mock_llm_invoke
        mock_get_llm.return_value = mock_llm

        from workflow import build_workflow
        workflow = build_workflow()

        state = initial_state()
        state['messages'] = [HumanMessage(content="Plan a 5-day Goa trip from Bangalore for a couple, budget 30000")]
        state['user_profile'] = {'name': 'Test User', 'user_id': 'test_user', 'email': 'test@example.com'}

        final_state = None
        step = 0
        for event in workflow.stream(state, {"recursion_limit": 20}):
            for node_name, node_state in event.items():
                if node_name == '__end__':
                    continue
                step += 1
                print(f"  Step {step}: {node_name} -> {node_state.get('current_step', '')}")
                final_state = node_state

                if node_state.get('pdf_status', {}).get('generated'):
                    print(f"  PDF: {node_state.get('pdf_path')}")
                    break

    print(f"\nWorkflow completed in {step} steps!")

    if final_state:
        prefs = final_state.get('trip_preferences', {})
        budget = final_state.get('budget_summary', {})
        pdf_path = final_state.get('pdf_path')

        if prefs.get('destination'):
            print(f"  Destination: {prefs['destination']}")
        if budget.get('total_inr'):
            print(f"  Total cost: Rs.{budget['total_inr']:,.0f}")
        if pdf_path:
            import os
            print(f"  PDF: {pdf_path} ({os.path.getsize(pdf_path):,} bytes)")

    print("\nFull workflow test PASSED!")


if __name__ == '__main__':
    test_full_workflow()
