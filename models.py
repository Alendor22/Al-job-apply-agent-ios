from __future__ import annotations
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict
from datetime import datetime

class CandidateProfile(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    location: str
    remote_ok: bool = True
    titles: List[str] = Field(default_factory=list)
    core_skills: List[str] = Field(default_factory=list)
    nice_skills: List[str] = Field(default_factory=list)
    min_salary: Optional[int] = None
    seniority: Optional[str] = None
    work_authorization: Optional[str] = None
    links: Dict[str, str] = Field(default_factory=dict)
    projects: List[Dict] = Field(default_factory=list)

class JobPosting(BaseModel):
    source: str
    company: str
    title: str
    location: Optional[str] = None
    url: HttpUrl
    description: str
    posted_at: Optional[datetime] = None
    raw: Dict = Field(default_factory=dict)

class RankedJob(BaseModel):
    job: JobPosting
    score: float
    reasons: List[str]
