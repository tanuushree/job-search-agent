# Job Scout — Learning Project

An after-work project to learn **LangGraph** and **AI agents** hands-on, by building a job-matching agent: upload a CV, get ranked real job openings back, scored 0–100 for fit.

Inspired by / reference: [Build your own Job Agent - Part 1 (Jam with AI)](https://jamwithai.substack.com/p/build-your-own-job-agent-part-1)

**This repo is built from scratch, not cloned.** The linked article is used purely as a reference to check against — the goal is understanding, not just a working copy.

---

## Why this project

A normal script always runs the same steps in the same order. An **agent** is a system where, at some point, *the model itself decides what happens next* — not a hardcoded rule. This project has exactly one such decision point (should we search again with a broader query, or stop?), and everything else is deliberately plain, inspectable code around that one flexible moment.

Goals for this build:
- Understand LangGraph's core mechanics (state, nodes, edges) by building them, not just reading about them
- Understand tool calling — the model choosing arguments, not the code hardcoding them
- Get hands-on with LLM observability (Opik) once there's an actual multi-step run worth watching
- End up with something genuinely useful for my own job search

---

## Core concepts (plain-language notes)

### Agent vs. workflow
A workflow always does the same steps in the same order. An agent has at least one point where the *model's own output* decides what happens next (e.g., loop back and search again, or stop). That's the line between the two.

### LangGraph's three building blocks
- **State** — one shared object passed between every step, like a clipboard everyone reads from and writes to. Holds things like: candidate profile, jobs found so far, ranked jobs, loop counter.
- **Nodes** — plain Python functions. Each takes the state, does one job, returns an update. No magic — just a function with a specific responsibility.
- **Edges** — the arrows deciding what runs next. Most are fixed. One here is a **conditional edge**: its destination is decided at runtime by looking at the state.

### Structured output / typed schemas
Instead of letting the model reply in loose free text, you force it to answer in a fixed shape (a schema/typed object). Benefits:
- Every downstream step gets guaranteed fields, no re-parsing or guessing
- If the model messes up the shape, it fails loudly right at that step — instead of quietly corrupting something three steps later
- A typed output is a *checkable* output — useful later for evaluation

### Tool calling
A **tool** is a function described to the model (name, purpose, expected arguments) — like a labeled button the model is allowed to press. **Binding** a tool means giving the model that menu of options. When the model "calls" a tool, it doesn't execute anything itself — it just replies with which tool and what arguments. Your code then actually runs it. This is what makes `fetch_jobs` feel like a real agent: the model decides the search query and filters, not your code.

### Bounded loops
The conditional edge checks: *"did we get enough strong matches?"* If not, and if we haven't already retried too many times, it loops back and searches again with a broader query. Two numbers keep this safe:
- A **quality bar** (e.g., "at least 5 jobs scoring 60+")
- A **hard cap** on retries (e.g., "never loop more than twice")

Without the cap, a bad match could loop forever, burning API calls for no benefit. General pattern: let the model decide, but always bound how much damage a bad decision can do.

### Observability (Opik)
- A **trace** = the full record of one run of the agent, start to finish.
- A **span** = one recorded chunk of work inside that trace. Each node becomes a span; each LLM/tool call inside it nests underneath.
- Opik wraps an already-built LangGraph graph and auto-generates the trace tree from one line, since LangGraph already knows its own structure.

### Baseline before fixing
Best practice demonstrated in the reference article: run the agent, honestly record what's wrong with it (weak filtering, loop not helping much, scores clustering too high, etc.), and *don't* fix anything yet. This gives real "before" numbers so later improvements can be proven, not just assumed.

---

## Decisions made so far

| Decision | Choice | Why |
|----------|--------|-----|
| Model provider | **Groq** (free tier) | No cost to experiment while learning |
| Groq model size | A larger, tool-calling-capable model (e.g. Llama 3.3 70B class), not a small/fast one | Smaller models are more likely to return malformed structured output |
| Package manager | **uv** | Fast, handles the virtual environment automatically, matches the reference article |
| Repo approach | Built from scratch | Learning > having a working copy on day one |
---

## Build order (why this order, not "build the graph first")

Building in an order where each piece is independently testable *before* wiring it into the graph — rather than writing the whole graph and debugging it as one tangled block.

1. **Environment + smoke test** — confirm the Groq API key + LangChain integration work with one plain "say hello" call. No LangGraph yet.
2. **`Profile` schema + CV extraction** — the one LLM call that runs *before* the graph starts. PDF text in, structured `Profile` object out. Fully testable in isolation with one fixture CV.
3. **`AgentState` shape** — define the shared clipboard (jobs found, ranked jobs, loop counter, etc.) — just the shape, no logic yet.
4. **One dumb node, no tools** — simplest possible graph: START → node → END, with a hardcoded search. Proves the LangGraph wiring works before adding intelligence.
5. **Swap in real tool-calling** — bind the `search_jobs` tool to the model, let it choose arguments, replacing the hardcoded version from step 4.
6. **Add ranking as a second node** — structured-output scoring, same pattern as step 2.
7. **Add the conditional edge** — the reformulation loop. Saved for last since it's trickiest to reason about, and easier once fetch → rank already runs reliably in a straight line.
8. **Wire in Opik** — added last, once there's an actual multi-step run worth tracing. This is also when a baseline batch (see "Baseline before fixing" above) becomes possible.

---

## Progress log

- [x] Decided on Groq + uv
- [x] Understood LangGraph core concepts (state, nodes, edges, conditional edges, tool calling)
- [x] Step 1: Environment setup + smoke test *(in progress)*
- [ ] Step 2: `Profile` schema + CV extraction
- [ ] Step 3: `AgentState` shape
- [ ] Step 4: Minimal dumb graph (START → node → END)
- [ ] Step 5: Real tool-calling for job search
- [ ] Step 6: Ranking node
- [ ] Step 7: Conditional edge / reformulation loop
- [ ] Step 8: Opik tracing + baseline batch

---

## Next steps

1. **Get a Groq API key** from console.groq.com, if not already done.
2. **Set up the project with `uv`**: initialize the project, add `langgraph`, `langchain-groq`, `pydantic`, `python-dotenv` as dependencies.
3. **Create `.env`** for the Groq API key and add it to `.gitignore` immediately.
4. **Write the smoke test**: load the key, make one plain model call, print the response. Nothing agent-related yet — just prove the setup works.
5. Once the smoke test passes → move to Step 2 (Profile schema + CV extraction).

---

## Reference

- Article: [Build your own Job Agent - Part 1](https://jamwithai.substack.com/p/build-your-own-job-agent-part-1) (Jam with AI, Shirin Khosravi Jam)
- Reference repo (for comparison only, not cloned): https://github.com/jamwithai/observable-job-agent
- Opik docs / signup: https://www.comet.com/signup