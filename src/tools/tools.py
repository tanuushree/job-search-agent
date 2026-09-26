import os
import requests
from dotenv import load_dotenv
from job_search_agent.schema import Job
from langchain_core.tools import tool

load_dotenv()

@tool
def search_jobs(query: str) -> list[Job]:
    """Search for live job listings.
    Returns a list of jobs, each with title, company, location, description, url, source.
    """
    app_id = os.getenv("ADZUNNA_APP_ID")
    app_key = os.getenv("ADZUNNA_API_KEY")
    app_url = os.getenv("ADZUNA_BASE_URL")

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": query,
        "content-type": "application/json"
    }

    response = requests.get(app_url, params=params)
    response.raise_for_status()
    data = response.json()

    jobs = []
    for result in data.get("results", []):
        job = Job(
            title=result.get("title", "Unknown"),
            company=result.get("company", {}).get("display_name", "Unknown"),
            location=result.get("location", {}).get("display_name"),
            description=result.get("description"),
            url=result.get("redirect_url"),
            source="Adzuna",
        )
        jobs.append(job)

    return [job.model_dump() for job in jobs]

if __name__ == "__main__":
    results = search_jobs.invoke({"query": "software engineer"})
    print(f"Found {len(results)} jobs\n")
    for job in results:
        print(f"{job['title']} — {job['company']} ({job['location']})")