from pydantic import BaseModel
from pydantic import ConfigDict
from typing import TypedDict


class Experience(BaseModel):
    model_config = ConfigDict(extra="forbid")
    company: str | None
    role: str | None
    duration_months: float | None
    description: str | None
    technologies: list[str] | None
    location: str | None

class Project(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None
    description: str | None
    technologies: list[str] | None
    link: str | None

class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None
    skills: list[str]
    years_of_experience: float | None
    languages: list[str] | None
    location: str | None
    current_role: str | None
    raw_summary: str | None
    experience: list[Experience]
    projects: list[Project]

class Job(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    company: str
    location: str | None = None
    description: str | None = None
    url: str | None = None
    source: str | None = None  # e.g. LinkedIn, etc


class AgentState(TypedDict, total=False):
    profile: Profile
    search_query: str | None       # search queries tried so far
    jobs_found: list[Job] | None         # actual job listings returned by the search tool
    ranked_jobs : list[Job] | None        # jobs ranked by the agent based on the profile
    retry_count: int | None
    llm_calls: int
    job_source: list[str]

