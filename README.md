# Al-job-apply-agent-ios
Personal Ai-Job-Search-agent-iOS
# JobSearch & Apply Assistant (Human-in-the-Loop)

This repo implements a compliant job-search + application-prep agent:
- Discovers jobs via **public** ATS job-board sources (Lever / Greenhouse Job Board).
- Ranks postings against your candidate profile.
- Generates an "application kit" (tailored bullets, cover letter draft, ATS keyword list).
- Tracks submissions in SQLite.
- Human-in-the-loop: it produces apply links and prefill data; **you** submit.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run discovery + ranking
python -m agent.cli discover --lever-orgs file:configs/lever_orgs.txt --greenhouse-boards file:configs/greenhouse_boards.txt

# Generate an application kit for a job (by URL or by internal job id)
python -m agent.cli kit --job-url "<apply-url>"
```

## Configuration
- `configs/candidate_profile.json`: your baseline profile
- `configs/lever_orgs.txt`: one Lever org slug per line (e.g. `stripe`)
- `configs/greenhouse_boards.txt`: one Greenhouse job board base URL per line
  - Example: `https://boards.greenhouse.io/mycompany`

## Notes on Safety/Compliance
- Avoid automating LinkedIn or other sites that prohibit automated activity.
- Prefer public job-board APIs (Lever Postings API, Greenhouse Job Board API).
