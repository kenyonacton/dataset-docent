# Dataset Docent

## A multi-agent onboarding guide for a living data science project

**Track: Freestyle**

---

## Video Demo

[Dataset Docent - Google x Kaggle AI Agents Intensive Capstone](https://www.youtube.com/watch?v=W5axsoqXC_I)

---

## The Problem

Documentation lies. Not intentionally, but it goes stale. A new analyst
joins a project, reads the README, and still has no idea where to start
or why anything was built the way it was.

The problem compounds on portfolio projects and open-source repos: there
is no one to ask, and the README only goes so far. Static documentation
has a second problem: projects change. A docent standing next to a fixed
museum exhibit works. A docent for a codebase or dataset that is actively
evolving needs to read the current state, not a snapshot.

Dataset Docent tests a simple idea: what if onboarding happened through
conversation? Ask the project a question, get an answer grounded in the
current spec and data. Not a chatbot bolted on afterward. The
documentation and the agent are the same system.

Dataset Docent is not domain-specific. The same architecture works for
any project where someone needs to understand both the data and the
decisions behind the code. CMS Open Payments is the example dataset here
because it is real, public, and has a natural "what looks unusual"
question built in. The agents, tools, and patterns are transferable.

---

## Why Agents

A single agent handling both data questions and design questions gets
confused. Ask it "what is the average payment?" and then "why did you
choose this architecture?" in the same context and it starts mixing
retrieval strategies. Routing those concerns to specialists keeps both
sharp.

There is a second reason: security. If one agent has access to
everything, the blast radius of a bad prompt is everything. Splitting
analyst tools from docs retrieval means a user who tries to extract
something they should not can only ever reach the analyst's whitelist.
The docs agent has no data access at all. Separation of concerns is also
separation of risk.

---

## The Data

CMS Open Payments is a federal dataset tracking payments from
pharmaceutical and medical device companies to physicians. It is real,
public, and compliance-relevant: the kind of data where knowing what
looks unusual is the entire point.

Dataset Docent runs exploratory analysis and z-score outlier detection
on a local sample. Z-score measures how far a value is from the mean in
units of standard deviation. A threshold of three is the standard
convention: roughly 99.7% of a normal distribution falls within three
standard deviations, so anything outside that is genuinely unusual. The
payment distribution has a long right tail, and z-score is more sensitive
to extreme outliers in that shape than IQR. That decision is documented
in ARCHITECTURE.md and the docs agent can explain it on request.

---

## Architecture

Three agents built with Google's Agent Development Kit (ADK):

**Orchestrator** routes each question to the right sub-agent. On first
message, it introduces the project and offers six suggested starting
questions. Typing "help" at any point repeats the welcome.

**Analyst** runs read-only pandas tools against the local CSV: summary
stats, top values by frequency, and z-score outlier detection. Every
tool enforces a column whitelist before touching the data, and results
are capped at 20 rows.

**Docs** reads SPEC.md, README.md, ARCHITECTURE.md, and QUESTIONS.md,
and answers questions about the project itself, citing the source file
and section in every response.

### Key Architectural Decisions

**Why three agents instead of one?** Separation of concerns and
separation of risk. A single agent mixing data retrieval and doc
retrieval produces worse answers to both. Splitting them also limits the
blast radius of any single prompt.

**Why enforce security in tool code rather than agent instructions?**
Instructions are suggestions to a language model. A whitelist check that
runs before any pandas call is a code guarantee. Asking the analyst about
a column called SocialSecurityNumber returns an error naming the allowed
columns. The agent cannot be talked past it because the check is not in
the prompt.

**Why load docs into context instead of a vector store?** At this scale,
the full documents fit comfortably in the context window and retrieval
precision is not a bottleneck. A vector store would add complexity
without meaningful benefit here.

**Why three narrow tools instead of one general run_pandas tool?** A
general tool is more flexible but less safe. Nothing outside the
whitelist is even expressible with narrow tools. The expressiveness vs.
safety tradeoff sits deliberately at the safe end for compliance-adjacent
data.

---

## What Was Built

- `dataset_docent/agent.py`: orchestrator and two sub-agents with routing
  logic and first-message welcome behavior
- `dataset_docent/tools.py`: three read-only pandas tools with column
  whitelist and 20-row caps
- `dataset_docent/open_payments_sample.csv`: local CMS Open Payments
  sample
- `SPEC.md`: written first, before any code; the docs agent serves it
- `ARCHITECTURE.md`: Mermaid diagram and Decisions section documenting
  six architectural choices with alternatives considered
- `QUESTIONS.md`: six suggested starting questions for reviewers
- `README.md`: setup instructions, architecture overview, usage guide

The spec was written before the code. The docs agent serves the spec.
The project documents itself through the same agent layer it uses to
analyze data.

---

## How It Was Built

Built spec-first in Antigravity with Gemini and ADK. SPEC.md came before
any code and constrained every implementation decision. ADK's dev web UI
(`adk web`) served as the interface throughout development and is the
primary demo surface. I can explain every architectural choice because
each one was made consciously, with an alternative considered and a
reason documented.

**Key concepts demonstrated:**
- Multi-agent system with ADK: orchestrator routing to specialist
  sub-agents
- Security features: column whitelist enforced in tool code, row caps,
  API key via environment variable, no credentials in the repository
- Agent skills and CLI: ADK dev web UI, `adk web` launch, Antigravity
  vibe coding workflow

---

## Setup

```bash
git clone https://github.com/kenyonacton/dataset-docent
cd dataset-docent
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
export GOOGLE_GENAI_USE_VERTEXAI=false
adk web
```

Open `http://localhost:8000`, start a new session, and type anything.
The docent introduces itself and offers starting points. Type "help" to
see them again at any time.

---

## What's Next

This submission is intentionally minimal. Planned expansion:

- Intent-aware change tracking: explaining why the project changed
  between versions, not just what changed
- Custom Streamlit frontend with clickable starter questions loaded
  before any message is sent
- BigQuery as the data backend replacing the local CSV
- MCP server exposure of the data and retrieval tools
- Full deployment to Cloud Run or Vertex AI Agent Engine

The architecture was designed with these additions in mind. None require
structural changes to what exists now.

---

## Project Link

https://github.com/kenyonacton/dataset-docent
