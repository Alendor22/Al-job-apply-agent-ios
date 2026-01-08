from __future__ import annotations
from typing import Tuple, List
from .models import CandidateProfile, JobPosting, RankedJob
import re

def _contains(text: str, needle: str) -> bool:
    return re.search(r"\b" + re.escape(needle.lower()) + r"\b", text) is not None

def score_job(job: JobPosting, profile: CandidateProfile) -> Tuple[float, List[str]]:
    text = (job.title + " " + job.description).lower()
    reasons: List[str] = []
    score = 0.0

    for skill in profile.core_skills:
        if skill and skill.lower() in text:
            score += 2.0
            reasons.append(f"Core skill: {skill}")

    for skill in profile.nice_skills:
        if skill and skill.lower() in text:
            score += 0.8
            reasons.append(f"Bonus: {skill}")

    for t in profile.titles:
        if t and t.lower() in job.title.lower():
            score += 1.5
            reasons.append(f"Title match: {t}")

    if profile.remote_ok and ("remote" in text or "distributed" in text or "anywhere" in text):
        score += 0.7
        reasons.append("Remote-friendly signals")

    # Rails+React synergy bonus
    if ("rails" in text or "ruby" in text) and "react" in text:
        score += 0.6
        reasons.append("Stack synergy: Rails + React")

    return score, reasons

def rank_jobs(jobs: List[JobPosting], profile: CandidateProfile, limit: int = 50) -> List[RankedJob]:
    ranked: List[RankedJob] = []
    for j in jobs:
        s, r = score_job(j, profile)
        ranked.append(RankedJob(job=j, score=s, reasons=r))
    ranked.sort(key=lambda x: x.score, reverse=True)
    return ranked[:limit]
