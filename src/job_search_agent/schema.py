from pydantic import BaseModel


class Experience(BaseModel):
    company: str | None
    role: str | None
    duration: float | None
    description: str | None
    technologies: list[str] | None
    location: str | None

class Project(BaseModel):
    name: str | None
    description: str | None
    technologies: list[str] | None
    link: str | None

class Profile(BaseModel):
    name: str | None
    skills: list[str]
    years_of_experience: float | None
    languages: list[str] | None
    location: str | None
    current_role: str | None
    raw_summary: str | None
    experience: list[Experience] | None
    projects: list[Project] | None