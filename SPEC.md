# SPEC: Dataset Docent

## Problem
New analysts (or project reviewers) joining a data project spend hours reading scattered docs and poking at unfamiliar data before they can ask a single useful question. This project tests a simple idea: onboard people through conversation. An agent answers questions about the data by running analysis, and answers questions about the project by serving this spec.

## Solution
A minimal multi-agent system built with Google's Agent Development Kit (ADK). The spec you are reading is both the design document and the docs agent's knowledge base. The project documents itself.

## Data
CMS Open Payments (healthcare compliance data), a small local CSV sample. Payments from drug and device companies to physicians. Chosen because it is public, real, and supports meaningful compliance questions (who gets paid, how much, and what looks unusual).

## Agents
1. **Orchestrator** (root agent). Routes each user question to the right sub-agent. Data questions go to the Analyst. Project, design, and "why" questions go to the Docs agent.
2. **Analyst** (sub-agent). Answers questions about the dataset by calling read-only pandas tools. Explains results in plain language.
3. **Docs** (sub-agent). Answers questions about the project itself by reading SPEC.md and README.md, loaded directly into context.

## Analyst tools
- `summary_stats(column)`: count, mean, median, min, max for a numeric column.
- `top_values(column, n)`: most frequent values in a column, default n=10, max 20.
- `find_outliers(column)`: rows where the z-score exceeds 3, capped at 20 rows. This is the compliance signal: unusually large payments.

## Security rules
- All tools are read-only. No writes, no deletes, no file access outside the data file.
- Column whitelist: tools accept only columns named in ALLOWED_COLUMNS. Anything else returns an error message, not data.
- Row caps: no tool returns more than 20 rows.
- The Gemini API key is read from the GOOGLE_API_KEY environment variable. It never appears in code or in the repo.

## Out of scope
Cloud deployment, BigQuery, MCP server, vector-store RAG, CI enforcement. This submission is intentionally minimal.

## Success criteria
A reviewer can clone the repo, run `adk web`, and get correct answers to: "What does this project do?", "What are the largest payments?", and "Which payments look unusual?"
