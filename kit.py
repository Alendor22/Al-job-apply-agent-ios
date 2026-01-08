from __future__ import annotations
from .models import CandidateProfile, JobPosting
from typing import Dict, List
import textwrap

def build_keyword_list(profile: CandidateProfile, job: JobPosting) -> List[str]:
    # naive: skills that appear in job text + all core skills
    text = (job.title + " " + job.description).lower()
    kws = []
    for s in profile.core_skills + profile.nice_skills:
        if s.lower() in text and s not in kws:
            kws.append(s)
    for s in profile.core_skills:
        if s not in kws:
            kws.append(s)
    return kws[:35]

def build_fit_bullets(profile: CandidateProfile, job: JobPosting) -> List[str]:
    bullets = []
    # Select project highlights that match job keywords
    text = (job.title + " " + job.description).lower()
    for proj in profile.projects:
        for h in proj.get("highlights", []):
            if any(k.lower() in text for k in ["rails","ruby","react","redux","jwt","oauth","postgres","sql","api"]):
                bullets.append(f"{proj['name']}: {h}")
    # De-dupe
    seen = set()
    out = []
    for b in bullets:
        if b not in seen:
            seen.add(b); out.append(b)
    return out[:8] if out else [
        "Built full-stack web applications using Ruby on Rails and JavaScript.",
        "Implemented authentication/authorization using JWT and OAuth2 flows.",
        "Designed REST APIs and integrated React front-ends for responsive UX."
    ]

def build_cover_letter(profile: CandidateProfile, job: JobPosting) -> str:
    bullets = build_fit_bullets(profile, job)
    paragraph = "\n".join([f"- {b}" for b in bullets[:4]])
    return textwrap.dedent(f"""
    Dear Hiring Team,

    I am applying for the {job.title} role. I build full-stack web applications with Ruby on Rails, JavaScript, React, and SQL databases, and I focus on clear communication, reliable delivery, and maintainable code.

    Relevant highlights:
    {paragraph}

    I would welcome the opportunity to discuss how I can contribute to your team.

    Sincerely,
    {profile.name}
    """).strip()

def build_application_kit(profile: CandidateProfile, job: JobPosting) -> Dict:
    return {
        "job": {
            "company": job.company,
            "title": job.title,
            "location": job.location,
            "url": str(job.url),
            "source": job.source
        },
        "fit_bullets": build_fit_bullets(profile, job),
        "keywords": build_keyword_list(profile, job),
        "cover_letter": build_cover_letter(profile, job)
    }
