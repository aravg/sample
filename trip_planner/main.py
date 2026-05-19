"""CLI entry point for the AI Trip Planner."""
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")
from langchain_core.messages import HumanMessage
from state import initial_state
from workflow import get_workflow


def run_trip_planner(query: str, user_name: str = "Traveler", user_id: str = "default") -> dict:
    """Run the full trip planning workflow and return the final state."""
    state = initial_state()
    state["messages"] = [HumanMessage(content=query)]
    state["user_profile"] = {
        "name": user_name,
        "user_id": user_id,
        "email": f"{user_id}@example.com",
    }

    workflow = get_workflow()
    print(f"\n{'='*60}")
    print("  AI TRIP PLANNER — Multi-Agent LangGraph System")
    print(f"{'='*60}")
    print(f"Query: {query}\n")

    step_count = 0
    max_steps = 30

    for event in workflow.stream(state, {"recursion_limit": max_steps}):
        for node_name, node_state in event.items():
            if node_name == "__end__":
                continue
            step_count += 1
            current = node_state.get("current_step", "")
            decision = node_state.get("orchestrator_decision", {})
            print(f"[Step {step_count}] Node: {node_name:<20} | Stage: {current:<25}", end="")
            if decision:
                print(f"| Next: {decision.get('next_step', '')}", end="")
            print()

            pdf_status = node_state.get("pdf_status", {})
            if pdf_status.get("generated"):
                pdf_path = node_state.get("pdf_path", "")
                print(f"\n[OK] PDF generated: {pdf_path}")
                return node_state

    print("\n[Workflow complete]")
    return state


def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        print("AI Trip Planner — Multi-Agent System")
        print("Enter your trip query (or press Enter for demo):")
        query = input("> ").strip()
        if not query:
            query = "Plan a 5-day trip to Goa from Bangalore for a couple, budget Rs.30,000. Need beach resort, nightlife, sightseeing, seafood. Prefer flights."

    result = run_trip_planner(query, user_name="Demo User", user_id="demo_user")

    print(f"\n{'='*60}")
    print("TRIP PLAN SUMMARY")
    print(f"{'='*60}")
    final_plan = result.get("final_plan", {}) or {}
    if final_plan:
        for k, v in final_plan.items():
            print(f"  {k.replace('_', ' ').title()}: {v}")
    budget = result.get("budget_summary", {})
    if budget:
        print(f"\n  Total Estimated Cost: Rs.{budget.get('total_inr', 0):,.0f}")
        print(f"  Per Person: Rs.{budget.get('per_person_inr', 0):,.0f}")

    pdf_path = result.get("pdf_path")
    if pdf_path:
        print(f"\n  PDF Report: {pdf_path}")
    else:
        errors = result.get("errors", [])
        if errors:
            print(f"\n  Errors: {errors}")


if __name__ == "__main__":
    main()
