# agentic-pm

**AI-assisted RAID analysis and stakeholder-tiered project status reporting.**

`agentic-pm` converts raw task data into structured RAID analysis, workstream RAG scoring, delivery predictability scores, and stakeholder-ready status reports — reducing weekly reporting from hours to seconds.

Built by a delivery manager, for delivery managers. Grounded in real programme delivery across ERP, cloud infrastructure, telecoms, and AI SaaS environments.

---

## The problem it solves

Every delivery manager maintains a RAID log. Most spend 2-4 hours every week turning that log into a status report, a steering committee summary, and a set of escalations — manually, from scratch, in a format that has to change depending on who is reading it.

`agentic-pm` automates that conversion. You maintain one task list. It produces the right report for the right audience in seconds.

---

## What it does

- Reads your task data (CSV, JSON, or pasted text)
- Scores each task as HIGH / MEDIUM / LOW risk based on status, blockers, and due dates
- Groups tasks by workstream and assigns an overall RAG (RED / AMBER / GREEN) per workstream
- Identifies Risks, Actions, Issues, and Decisions from the task data automatically
- Calculates a delivery predictability score (0-100)
- Produces a stakeholder-tiered status report in three formats:
  - **Delivery** — full task-level detail, all blockers, recommended actions
  - **Executive** — one paragraph per workstream, key risks and decisions only
  - **Board** — three sentences, overall RAG, single biggest risk, single decision required

---

## Why it exists

The 82% to 95% delivery predictability improvement documented across regulated infrastructure programmes came from consistent, structured status reporting — not heroics. The discipline of weekly RAID analysis and stakeholder-appropriate communication is what keeps programmes on track.

`agentic-pm` makes that discipline repeatable and low-effort, regardless of programme size or team experience.

---

## Quickstart (command line)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here

# Generate sample data and run
python agentic_pm.py --sample
python agentic_pm.py --input sample_tasks.csv

# Executive-level report
python agentic_pm.py --input sample_tasks.csv --stakeholder executive

# Board-level report
python agentic_pm.py --input sample_tasks.csv --stakeholder board
```

## Web app

A hosted web version is available at **[agentic-pm.onrender.com](https://agentic-pm.onrender.com)**

Features:
- CSV upload or manual task entry
- Workstream RAG dashboard
- Export as Word (.doc), plain text (.txt), or PDF
- No installation required

---

## Input format

CSV with columns: `Workstream`, `Task name`, `Owner`, `Due date`, `Status`, `Blockers`

Or pipe-separated text: `Workstream | Task name | Owner | Due date | Status | Blockers`

**Status values:** `Complete` | `In Progress` | `At Risk` | `Not Started`

---

## Risk scoring logic

| Condition | Risk level |
|-----------|-----------|
| Status = Complete | LOW |
| Status = At Risk | HIGH |
| Any blocker present (not None/N/A) | HIGH |
| Due date within 7 days and not complete | HIGH |
| Due date within 14 days | MEDIUM |
| Status = Not Started with due date within 21 days | MEDIUM |
| Everything else | LOW |

**Workstream RAG** = RED if any HIGH risk task exists / AMBER if any MEDIUM / GREEN if all LOW.

---

## Output

- Workstream RAG summary per workstream
- Full RAID-structured weekly status report
- Delivery predictability score with calculation breakdown
- Steering committee summary paragraph
- Escalation and decisions required section

---

## Requirements

- Python 3.9+
- Anthropic API key (set as `ANTHROPIC_API_KEY` environment variable)

## Roadmap

- [ ] Azure DevOps native export parser
- [ ] Jira CSV export parser
- [ ] Slack / Teams notification integration
- [ ] Power BI dashboard export
- [ ] Multi-workstream dependency mapping
- [ ] Historical predictability trend tracking

## Contributing

Pull requests welcome. Please open an issue first to discuss what you would like to change.

## Licence

MIT — see [LICENSE](LICENSE)

---

*Part of an open-source toolkit for AI-assisted project delivery.*
*See also: [cutover-copilot](https://github.com/TemitopeKadri/cutover-copilot) | [erp-discovery-agent](https://github.com/TemitopeKadri/erp-discovery-agent) | [prince2-agile-templates](https://github.com/TemitopeKadri/prince2-agile-templates)*
