# agentic-pm

**AI-assisted project status reporting, RAID analysis, and stakeholder summaries.**

`agentic-pm` ingests your project task data and uses an LLM to produce structured, stakeholder-ready outputs — weekly RAID packs, slippage-risk scores per workstream, and steering committee summaries — without requiring manual write-up.

Built by a delivery manager, for delivery managers.

---

## What it does

- Reads a CSV or JSON task export (Jira, Azure DevOps, or manual)
- Scores each workstream for slippage risk based on status, due dates, and blockers
- Produces a RAID-style weekly status pack in plain text or Markdown
- Generates a one-paragraph steering committee summary, tiered by stakeholder level

## Why it exists

The 82% → 95% delivery predictability improvement documented in regulated infrastructure programmes came from consistent, structured status reporting — not heroics. This tool makes that discipline repeatable and low-effort.

## Quickstart

```bash
pip install -r requirements.txt
python agentic_pm.py --input sample_tasks.csv --output status_pack.md
```

## Input format

CSV with columns: `task_id`, `workstream`, `task_name`, `owner`, `due_date`, `status`, `blockers`

Status values: `Not Started` | `In Progress` | `At Risk` | `Complete`

## Output

- `status_pack.md` — full RAID-style weekly status report
- Console summary — one-paragraph steering committee briefing

## Requirements

- Python 3.9+
- Anthropic API key (set as `ANTHROPIC_API_KEY` environment variable)

## Roadmap

- [ ] Azure DevOps native export parser
- [ ] Jira CSV export parser  
- [ ] Slack/Teams notification integration
- [ ] Power BI dashboard export
- [ ] Multi-workstream dependency mapping

## Contributing

Pull requests welcome. Please open an issue first to discuss what you'd like to change.

## Licence

MIT — see [LICENSE](LICENSE)

---

*Part of an open-source toolkit for AI-assisted project delivery. See also: [cutover-copilot](https://github.com/TemitopeKadri/cutover-copilot), [erp-discovery-agent](https://github.com/TemitopeKadri/erp-discovery-agent), [prince2-agile-templates](https://github.com/TemitopeKadri/prince2-agile-templates)*
