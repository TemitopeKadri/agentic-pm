"""
agentic-pm: AI-assisted project status reporting and RAID analysis.
https://github.com/TemitopeKadri/agentic-pm

Usage:
    python agentic_pm.py --input sample_tasks.csv --output status_pack.md
    python agentic_pm.py --input sample_tasks.csv --stakeholder executive

MIT Licence — Copyright (c) 2026 Temitope Kadri
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, date
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)


# ── Risk scoring ──────────────────────────────────────────────────────────────

def score_task_risk(task: dict) -> str:
    """Return HIGH / MEDIUM / LOW risk based on status, due date, and blockers."""
    status = task.get("status", "").strip().lower()
    blockers = task.get("blockers", "").strip()
    due_raw = task.get("due_date", "").strip()

    if status == "complete":
        return "LOW"

    # Parse due date
    days_remaining = None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            due_date = datetime.strptime(due_raw, fmt).date()
            days_remaining = (due_date - date.today()).days
            break
        except ValueError:
            continue

    has_blocker = bool(blockers and blockers.lower() not in ("", "none", "n/a", "-"))

    if status == "at risk" or has_blocker:
        return "HIGH"
    if days_remaining is not None and days_remaining < 7:
        return "HIGH"
    if days_remaining is not None and days_remaining < 14:
        return "MEDIUM"
    if status == "not started" and days_remaining is not None and days_remaining < 21:
        return "MEDIUM"
    return "LOW"


def summarise_workstreams(tasks: list[dict]) -> dict:
    """Group tasks by workstream and compute RAG per workstream."""
    workstreams: dict[str, dict] = {}
    for task in tasks:
        ws = task.get("workstream", "General").strip()
        if ws not in workstreams:
            workstreams[ws] = {"tasks": [], "risk_counts": {"HIGH": 0, "MEDIUM": 0, "LOW": 0}}
        risk = score_task_risk(task)
        task["_risk"] = risk
        workstreams[ws]["tasks"].append(task)
        workstreams[ws]["risk_counts"][risk] += 1

    # Overall RAG per workstream
    for ws, data in workstreams.items():
        rc = data["risk_counts"]
        if rc["HIGH"] > 0:
            data["rag"] = "RED"
        elif rc["MEDIUM"] > 0:
            data["rag"] = "AMBER"
        else:
            data["rag"] = "GREEN"

    return workstreams


# ── LLM call ──────────────────────────────────────────────────────────────────

def call_claude(prompt: str) -> str:
    """Call Claude API and return the text response."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_raid_pack(workstreams: dict, stakeholder: str = "delivery") -> str:
    """Generate a RAID-style status pack using Claude."""
    ws_summary = []
    for ws, data in workstreams.items():
        tasks_text = "\n".join(
            f"  - [{t['_risk']}] {t.get('task_name','')} | Owner: {t.get('owner','')} "
            f"| Due: {t.get('due_date','')} | Status: {t.get('status','')} "
            f"| Blockers: {t.get('blockers','None')}"
            for t in data["tasks"]
        )
        ws_summary.append(
            f"Workstream: {ws} | Overall RAG: {data['rag']}\n{tasks_text}"
        )

    ws_block = "\n\n".join(ws_summary)
    today = date.today().strftime("%d %B %Y")

    stakeholder_instructions = {
        "delivery": "Write for the delivery team lead. Include all task-level detail, blockers, and recommended actions.",
        "executive": "Write for a senior executive or steering committee. One paragraph per workstream. Focus on RAG status, key risks, and decisions required. No task-level detail.",
        "board": "Write for a board-level audience. Three sentences maximum total. Overall programme RAG, single biggest risk, single recommended decision.",
    }

    instruction = stakeholder_instructions.get(
        stakeholder.lower(),
        stakeholder_instructions["delivery"]
    )

    prompt = f"""You are an expert project manager producing a weekly status report.

Date: {today}
Stakeholder level: {stakeholder.upper()}
Instruction: {instruction}

Project task data:
{ws_block}

Produce:
1. A RAID-style weekly status pack with sections: Summary, Risks, Actions, Issues, Decisions Required
2. A delivery predictability score (0-100) based on the ratio of on-track to at-risk tasks
3. A one-paragraph steering committee summary

Format the output in clean Markdown. Be direct and specific. Do not use filler phrases."""

    return call_claude(prompt)


# ── File I/O ──────────────────────────────────────────────────────────────────

def load_tasks(input_path: str) -> list[dict]:
    """Load tasks from CSV or JSON."""
    path = Path(input_path)
    if not path.exists():
        print(f"Error: input file not found: {input_path}")
        sys.exit(1)

    if path.suffix.lower() == ".json":
        with open(path) as f:
            data = json.load(f)
        return data if isinstance(data, list) else data.get("tasks", [])

    # CSV
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_output(content: str, output_path: str | None) -> None:
    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
        print(f"\nStatus pack written to: {output_path}")
    else:
        print("\n" + "═" * 60)
        print(content)
        print("═" * 60)


# ── Sample data ───────────────────────────────────────────────────────────────

SAMPLE_CSV = """task_id,workstream,task_name,owner,due_date,status,blockers
T001,ERP Migration,Complete data mapping for GL accounts,Tope,15/06/2026,In Progress,Awaiting sign-off from Finance
T002,ERP Migration,UAT sign-off — Accounts Payable module,Sarah,10/06/2026,At Risk,Test environment unstable
T003,Infrastructure,Firewall rule changes for new data centre,Dev,20/06/2026,In Progress,None
T004,Infrastructure,Network cutover rehearsal,Dev,25/06/2026,Not Started,None
T005,Change Management,Training delivery — Wave 1 users,Marcus,12/06/2026,In Progress,None
T006,Change Management,Go-live comms pack approved,Marcus,08/06/2026,At Risk,Comms director on leave
T007,Governance,Steering committee pack — June,Tope,05/06/2026,Complete,None
T008,Governance,Risk register updated post-rehearsal,Tope,18/06/2026,Not Started,None
"""


def create_sample(output_path: str = "sample_tasks.csv") -> None:
    Path(output_path).write_text(SAMPLE_CSV, encoding="utf-8")
    print(f"Sample tasks file created: {output_path}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="agentic-pm: AI-assisted project status reporting and RAID analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agentic_pm.py --sample
  python agentic_pm.py --input sample_tasks.csv
  python agentic_pm.py --input sample_tasks.csv --output status_pack.md
  python agentic_pm.py --input sample_tasks.csv --stakeholder executive
        """
    )
    parser.add_argument("--input", help="Path to tasks CSV or JSON file")
    parser.add_argument("--output", help="Path to write Markdown status pack (optional)")
    parser.add_argument("--stakeholder", default="delivery",
                        choices=["delivery", "executive", "board"],
                        help="Stakeholder level for the report (default: delivery)")
    parser.add_argument("--sample", action="store_true",
                        help="Generate a sample_tasks.csv file and exit")

    args = parser.parse_args()

    if args.sample:
        create_sample()
        return

    if not args.input:
        parser.print_help()
        return

    print(f"Loading tasks from: {args.input}")
    tasks = load_tasks(args.input)
    print(f"Loaded {len(tasks)} tasks")

    workstreams = summarise_workstreams(tasks)
    print(f"Analysed {len(workstreams)} workstreams")

    # Print workstream RAG to console
    print("\nWorkstream RAG:")
    for ws, data in workstreams.items():
        rag = data["rag"]
        symbol = "🔴" if rag == "RED" else "🟡" if rag == "AMBER" else "🟢"
        print(f"  {symbol} {ws}: {rag} ({data['risk_counts']['HIGH']} HIGH, "
              f"{data['risk_counts']['MEDIUM']} MEDIUM, {data['risk_counts']['LOW']} LOW)")

    print(f"\nGenerating {args.stakeholder.upper()} status pack via Claude API...")
    report = generate_raid_pack(workstreams, stakeholder=args.stakeholder)
    write_output(report, args.output)


if __name__ == "__main__":
    main()
