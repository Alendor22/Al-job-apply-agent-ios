from __future__ import annotations
import argparse, asyncio, json
from pathlib import Path
from rich import print
from .models import CandidateProfile
from .sources import fetch_lever, fetch_greenhouse
from .ranker import rank_jobs
from .kit import build_application_kit
from .tracker import Tracker

def _read_list_arg(val: str) -> list[str]:
    if val.startswith("file:"):
        p = Path(val.replace("file:", "", 1))
        lines = [l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip() and not l.strip().startswith("#")]
        return lines
    return [x.strip() for x in val.split(",") if x.strip()]

async def _discover(lever_orgs: list[str], greenhouse_boards: list[str]) -> list[dict]:
    jobs = []
    for org in lever_orgs:
        try:
            jobs.extend([j.model_dump() for j in await fetch_lever(org)])
        except Exception as e:
            print(f"[yellow]Lever fetch failed for {org}: {e}[/yellow]")
    for board in greenhouse_boards:
        try:
            jobs.extend([j.model_dump() for j in await fetch_greenhouse(board)])
        except Exception as e:
            print(f"[yellow]Greenhouse fetch failed for {board}: {e}[/yellow]")
    return jobs

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("discover", help="Discover and rank jobs")
    d.add_argument("--profile", default="configs/candidate_profile.json")
    d.add_argument("--lever-orgs", default="file:configs/lever_orgs.txt")
    d.add_argument("--greenhouse-boards", default="file:configs/greenhouse_boards.txt")
    d.add_argument("--db", default="agent.db")
    d.add_argument("--limit", type=int, default=25)

    k = sub.add_parser("kit", help="Generate an application kit for a job URL already in the DB")
    k.add_argument("--profile", default="configs/candidate_profile.json")
    k.add_argument("--job-url", required=True)
    k.add_argument("--db", default="agent.db")

    args = ap.parse_args()

    profile = CandidateProfile.model_validate_json(Path(args.profile).read_text(encoding="utf-8"))
    tracker = Tracker(args.db)
    tracker.init()

    if args.cmd == "discover":
        lever_orgs = _read_list_arg(args.lever_orgs)
        greenhouse_boards = _read_list_arg(args.greenhouse_boards)

        jobs = asyncio.run(_discover(lever_orgs, greenhouse_boards))
        for j in jobs:
            tracker.upsert_job(j)

        # Rank in-memory
        from .models import JobPosting
        job_objs = [JobPosting(**j) for j in jobs]
        ranked = rank_jobs(job_objs, profile, limit=args.limit)

        print(f"\n[bold]Top {len(ranked)} matches[/bold]\n")
        for i, r in enumerate(ranked, 1):
            print(f"[{i}] [bold]{r.job.title}[/bold] — {r.job.company} ({r.job.source})")
            print(f"    {r.job.url}")
            if r.job.location:
                print(f"    Location: {r.job.location}")
            if r.reasons:
                print(f"    Reasons: {', '.join(r.reasons[:5])}")
            print(f"    Score: {r.score:.2f}\n")

    elif args.cmd == "kit":
        # Read job from DB
        import sqlite3
        conn = sqlite3.connect(args.db)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM jobs WHERE url=?", (args.job_url,)).fetchone()
        if not row:
            raise SystemExit("Job URL not found in DB. Run discover first or insert the job manually.")
        job = dict(row)
        from .models import JobPosting
        job_obj = JobPosting(
            source=job["source"],
            company=job["company"],
            title=job["title"],
            location=job.get("location"),
            url=job["url"],
            description=job.get("description") or "",
            posted_at=None,
            raw={}
        )
        kit = build_application_kit(profile, job_obj)
        out = Path("application_kit.json")
        out.write_text(json.dumps(kit, indent=2), encoding="utf-8")
        print(f"[green]Wrote {out}[/green]")
        print("\nCover letter draft:\n")
        print(kit["cover_letter"])

if __name__ == "__main__":
    main()
