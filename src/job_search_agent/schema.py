from pydantic import BaseModel
from pydantic import ConfigDict


class Experience(BaseModel):
    model_config = ConfigDict(extra="forbid")
    company: str | None
    role: str | None
    duration: float | None
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