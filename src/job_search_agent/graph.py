import os

from langchain_groq import ChatGroq

from langgraph.graph import StateGraph, START, END
from job_search_agent.schema import AgentState
from job_search_agent import extract_profile, extract_pdf
from tools.tools import search_jobs


# def dummy(state: AgentState) -> dict:
#     return {"search_query": "dummy string"}

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
        "openings that fit this candidate."
    )
 
    response = llm_with_tools.invoke(prompt)
 
    jobs_found = []
    search_query = None
    for call in response.tool_calls:
        if call["name"] == "search_jobs":
            search_query = call["args"].get("query")
            jobs_found = search_jobs.invoke(call["args"])
 
    return {
        "search_query": search_query,
        "jobs_found": jobs_found,
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


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

    print(result)