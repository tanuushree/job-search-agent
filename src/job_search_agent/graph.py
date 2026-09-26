import os

from langchain_groq import ChatGroq

from langgraph.graph import StateGraph, START, END
from job_search_agent.schema import AgentState
from job_search_agent import extract_profile, extract_pdf
from tools.tools import search_jobs


# Ordered preference, most preferred first. This is a sort, not a filter —
# jobs from other Indian cities still come back, just ranked lower.
LOCATION_PREFERENCE = ["mumbai", "pune", "bengaluru", "bangalore"]

def _location_rank(job: dict) -> int:
    """Lower rank = higher preference. Jobs matching no preferred city
    keep their original relative order after the preferred ones (stable sort)."""
    location = (job.get("location") or "").lower()
    for rank, city in enumerate(LOCATION_PREFERENCE):
        if city in location:
            return rank
    return len(LOCATION_PREFERENCE) 

def search_job(state: AgentState) -> dict:
    """The real step-5 node: the model itself decides the search query
    (and calls the search_jobs tool), instead of us hardcoding it."""

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    llm_with_tools = llm.bind_tools([search_jobs])
 
    profile = state["profile"]
    prompt = (
        "Here is a candidate profile:\n"
        f"{profile.model_dump_json(indent=2)}\n\n"
        "Call search_jobs with the single best search query to find job "
        "openings that fit this candidate. Job search engines match "
        "queries literally, similar to a search engine — keep the query "
        "short and realistic, like a real job title a recruiter would post "
        "(2-4 words, e.g. 'Full Stack Developer' or 'Backend Engineer "
        "Node.js'). Do not string together the candidate's entire skill "
        "list, and do not include any city or location in the query — the "
        "search covers the whole country and location handling happens "
        "separately."
    )
 
    response = llm_with_tools.invoke(prompt)
 
    jobs_found = []
    search_query = None
    for call in response.tool_calls:
        if call["name"] == "search_jobs":
            search_query = call["args"].get("query")
            jobs_found = search_jobs.invoke(call["args"])
 
    # Sort nationwide results so Mumbai > Pune > Bengaluru come first,
    # without dropping jobs from anywhere else in India.
    jobs_found = sorted(jobs_found, key=_location_rank)

    return {
        "search_query": search_query,
        "jobs_found": jobs_found,
        "llm_calls": state.get("llm_calls", 0) + 1,
    }

def print_jobs_table(jobs: list[dict]) -> None:
    """Print jobs_found as a plain formatted table (no extra dependencies)."""
    if not jobs:
        print("No jobs found.")
        return
 
    def truncate(text: str, width: int) -> str:
        text = text or ""
        return text if len(text) <= width else text[: width - 1] + "…"
 
    title_w, company_w, location_w = 35, 25, 20
 
    header = f"{'TITLE':<{title_w}} {'COMPANY':<{company_w}} {'LOCATION':<{location_w}} URL"
    print(header)
    print("-" * len(header))
 
    for job in jobs:
        title = truncate(job.get("title"), title_w)
        company = truncate(job.get("company"), company_w)
        location = truncate(job.get("location"), location_w)
        url = job.get("url") or ""
        print(f"{title:<{title_w}} {company:<{company_w}} {location:<{location_w}} {url}")

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("search_job", search_job)
    graph.add_edge(START, "search_job")
    graph.add_edge("search_job", END)
    return graph.compile()


if __name__ == "__main__":
    from job_search_agent.schema import Profile

    text = extract_pdf()
    profile = extract_profile(text) 

    starting_state = {"profile": profile}

    app = build_graph()
    result = app.invoke(starting_state)

    print_jobs_table(result["jobs_found"])