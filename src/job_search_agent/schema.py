from groq import BaseModel


class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: float | None = None
    description: str | None = None
    technologies: list[str] | None = []
    location: str | None = None

class Project(BaseModel):
    name: str | None = None
    description: str | None = None
    technologies: list[str] | None = []
    link: str | None = None

class Profile(BaseModel):
    name: str | None = None
    skills: list[str]
    years_of_experience: float | None = None
    languages: list[str] | None = ['English']
    location: str | None = 'India'
    current_role: str | None = 'Software Engineer'
    raw_summary: str | None = None
    experience: list[Experience] | None = []
    projects: list[Project] | None = []