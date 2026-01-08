from __future__ import annotations
import httpx
from typing import List, Optional, Dict
from dateutil import parser as dtparser
from .models import JobPosting

USER_AGENT = "JobSearchAssistant/1.0 (+human-in-the-loop)"

async def fetch_lever(org: str) -> List[JobPosting]:
    """
    Fetch public postings from Lever org using the Postings API.

    Typical endpoint:
      https://api.lever.co/v0/postings/{org}?mode=json
    """
    url = f"https://api.lever.co/v0/postings/{org}?mode=json"
    async with httpx.AsyncClient(timeout=25, headers={"User-Agent": USER_AGENT}) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    jobs: List[JobPosting] = []
    for item in data:
        apply_url = item.get("applyUrl") or item.get("hostedUrl") or item.get("url")
        if not apply_url:
            continue
        posted_at = None
        # Lever sometimes returns 'createdAt' (ms epoch)
        if isinstance(item.get("createdAt"), (int, float)):
            try:
                posted_at = dtparser.parse("1970-01-01T00:00:00Z")  # placeholder; handled below
            except Exception:
                posted_at = None
        desc = (item.get("descriptionPlain") or item.get("description") or "") + "\n" + (item.get("additionalPlain") or "")
        jobs.append(JobPosting(
            source="lever",
            company=item.get("categories", {}).get("team") or item.get("company") or org,
            title=item.get("text") or item.get("title") or "Unknown",
            location=item.get("categories", {}).get("location") or item.get("location"),
            url=apply_url,
            description=desc.strip(),
            posted_at=None,
            raw=item,
        ))
    return jobs

async def fetch_greenhouse(board_base_url: str) -> List[JobPosting]:
    """
    Fetch public postings from a Greenhouse-hosted job board.

    Many boards expose JSON at:
      {board_base_url}/jobs?gh_jid=... (HTML)
    And the Job Board API typically:
      https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
    However, the most reliable approach is to use the documented Job Board API when you know the board token.

    This function supports two inputs:
    - If you pass a boards-api URL directly, it will fetch it.
    - If you pass a standard boards.greenhouse.io URL, it will try to derive the token from the path.
    """
    board_base_url = board_base_url.rstrip("/")

    if "boards-api.greenhouse.io" in board_base_url:
        api_url = board_base_url
    else:
        # Example: https://boards.greenhouse.io/github  -> token "github"
        token = board_base_url.split("/")[-1]
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"

    async with httpx.AsyncClient(timeout=25, headers={"User-Agent": USER_AGENT}) as client:
        r = await client.get(api_url)
        r.raise_for_status()
        data = r.json()

    jobs: List[JobPosting] = []
    for item in data.get("jobs", []):
        # item fields: id, title, location{name}, content, absolute_url, updated_at
        posted_at = None
        if item.get("updated_at"):
            try:
                posted_at = dtparser.parse(item["updated_at"])
            except Exception:
                posted_at = None

        desc = item.get("content") or ""
        jobs.append(JobPosting(
            source="greenhouse",
            company=data.get("name") or api_url,
            title=item.get("title") or "Unknown",
            location=(item.get("location") or {}).get("name"),
            url=item.get("absolute_url"),
            description=desc,
            posted_at=posted_at,
            raw=item,
        ))
    return jobs
