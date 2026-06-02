"""
agentic-pm web server
https://github.com/TemitopeKadri/agentic-pm
MIT Licence — Copyright (c) 2026 Temitope Kadri
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import anthropic
import os

app = Flask(__name__, static_folder="static")
CORS(app)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/analyse", methods=["POST"])
def analyse():
    data = request.json
    tasks = data.get("tasks", [])
    stakeholder = data.get("stakeholder", "delivery")
    project_name = data.get("projectName", "Project")
    today = data.get("today", "")

    if not tasks:
        return jsonify({"error": "No tasks provided"}), 400

    # Build workstream groups
    ws_groups = {}
    for t in tasks:
        ws = t.get("workstream", "General")
        if ws not in ws_groups:
            ws_groups[ws] = []
        ws_groups[ws].append(t)

    ws_block = "\n\n".join(
        f"Workstream: {ws} | RAG: {_rag(ts)}\n" +
        "\n".join(
            f"  - [{_risk(t)}] {t.get('task','')} | Owner: {t.get('owner','')} | "
            f"Due: {t.get('due','')} | Status: {t.get('status','')} | Blockers: {t.get('blockers','None')}"
            for t in ts
        )
        for ws, ts in ws_groups.items()
    )

    instructions = {
        "delivery": "Write for the delivery team lead. Include all task-level detail, blockers, and recommended actions.",
        "executive": "Write for a senior executive or steering committee. One paragraph per workstream. Focus on RAG status, key risks, and decisions required. No task-level detail.",
        "board": "Write for a board-level audience. Three sentences maximum total. Overall programme RAG, single biggest risk, single recommended decision."
    }

    prompt = f"""You are an expert project manager producing a weekly status report.

Project: {project_name}
Date: {today}
Stakeholder level: {stakeholder.upper()}
Instruction: {instructions.get(stakeholder, instructions['delivery'])}

Project task data:
{ws_block}

Produce:
1. A RAID-style weekly status pack with sections: Summary, Risks, Actions, Issues, Decisions Required
2. A delivery predictability score (0-100) based on ratio of on-track to at-risk tasks
3. A steering committee summary paragraph

Format in clean plain text with ## headings. Be direct and specific. Do not use filler phrases."""

    try:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"report": message.content[0].text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _risk(task):
    s = task.get("status", "").lower()
    b = task.get("blockers", "").lower()
    if s == "complete": return "LOW"
    if s == "at risk" or (b and b not in ("none", "", "-")): return "HIGH"
    if s == "not started": return "MEDIUM"
    return "LOW"


def _rag(tasks):
    risks = [_risk(t) for t in tasks]
    if "HIGH" in risks: return "RED"
    if "MEDIUM" in risks: return "AMBER"
    return "GREEN"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
