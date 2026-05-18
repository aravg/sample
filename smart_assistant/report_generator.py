import json
import os
from datetime import datetime

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


class ReportGenerator:
    def __init__(self):
        os.makedirs(REPORTS_DIR, exist_ok=True)

    def generate(
        self,
        query: str,
        selected_agents: list[str],
        agent_results: dict,
        final_response: str,
    ) -> str:
        now = datetime.now()
        timestamp_file = now.strftime("%Y_%m_%d_%H_%M_%S")
        timestamp_display = now.strftime("%Y-%m-%d %H:%M:%S")

        txt_path = os.path.join(REPORTS_DIR, f"report_{timestamp_file}.txt")
        json_path = os.path.join(REPORTS_DIR, f"report_{timestamp_file}.json")

        self._write_txt(txt_path, query, selected_agents, agent_results, final_response, timestamp_display)
        self._write_json(json_path, query, selected_agents, agent_results, final_response, timestamp_display)

        return txt_path

    def _write_txt(self, path, query, agents, results, final, timestamp):
        lines = [
            "=" * 70,
            "  SMART PERSONAL ASSISTANT — EXECUTION REPORT",
            "=" * 70,
            f"Execution Date & Time : {timestamp}",
            f"User Query            : {query}",
            f"Selected Agents       : {', '.join(agents) if agents else 'None (general response)'}",
            "",
            "-" * 70,
            "AGENT RESPONSES & API OUTPUTS",
            "-" * 70,
        ]

        for agent_name, result in results.items():
            lines.append(f"\n[{agent_name.upper()} AGENT]")
            lines.append(f"  Status  : {result.get('status', 'unknown')}")
            if result.get("status") == "success":
                processed = result.get("processed", {})
                lines.append("  Processed Data:")
                for key, val in processed.items():
                    if isinstance(val, dict):
                        lines.append(f"    {key}:")
                        for k2, v2 in val.items():
                            lines.append(f"      {k2}: {v2}")
                    elif isinstance(val, list):
                        lines.append(f"    {key}: {', '.join(str(v) for v in val)}")
                    else:
                        lines.append(f"    {key}: {val}")
                lines.append("  Raw API Output:")
                raw = json.dumps(result.get("raw_data", {}), indent=4)
                for raw_line in raw.splitlines():
                    lines.append(f"    {raw_line}")
            else:
                lines.append(f"  Error   : {result.get('error', 'Unknown error')}")

        lines += [
            "",
            "-" * 70,
            "FINAL COMBINED RESPONSE",
            "-" * 70,
            final,
            "",
            "=" * 70,
            "END OF REPORT",
            "=" * 70,
        ]

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _write_json(self, path, query, agents, results, final, timestamp):
        payload = {
            "execution_timestamp": timestamp,
            "user_query": query,
            "selected_agents": agents,
            "agent_results": results,
            "final_response": final,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
