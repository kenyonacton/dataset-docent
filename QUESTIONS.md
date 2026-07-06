# Reviewer Questions and Answers

This document lists key design and implementation questions for reviewers, providing context on technical decisions.

## Question 1: Why sub-agents instead of one agent?
We use a multi-agent system (Orchestrator routing to Analyst and Docs) to isolate concerns. This prevents prompt bloat and keeps agent scopes focused. The Analyst agent only handles data-related tasks and has access to python analysis tools, while the Docs agent focus purely on interpreting project files. This minimizes distraction and reduces token usage per turn.

## Question 2: Why enforce security in tool code rather than agent instructions?
LLM instructions are suggestions that can be bypassed by prompt injection or hallucinations. Code constraints (such as column whitelists and row limits in `tools.py`) are hard programmatic guarantees. Checking column names and enforcing `min(n, 20)` in Python ensures security regardless of the LLM state.

## Question 3: Why load docs into context instead of a vector store?
The project documentation (SPEC, README, ARCHITECTURE) is small enough to fit directly in the Gemini context window. Loading documents into context ensures 100% recall and allows the model to reason over the entire project structure comprehensively, avoiding the chunking errors, retrieval failures, and setup complexity of a Vector DB / RAG system.

## Question 4: Why three narrow tools instead of one general run_pandas tool?
Exposing a generic tool like `run_pandas` or a raw Python execution environment creates a massive security vulnerability. Narrow, pre-defined tools (`summary_stats`, `top_values`, `find_outliers`) allow strict validation of column names and parameter bounds, ensuring that only read-only, non-destructive compliance operations can execute.

## Question 5: Why Mermaid for the diagram?
Mermaid allows us to define diagrams as code. It renders natively in platforms like GitHub and is easy to update directly within markdown files. This ensures that documentation and diagrams stay in sync as the system evolves.

## Question 6: What statistical method detects outliers and why?
We use the Z-score method with a threshold of 3. This identifies records that lie more than 3 standard deviations away from the mean, which is standard for highlighting extreme compliance signals in normally (or near-normally) distributed data.
