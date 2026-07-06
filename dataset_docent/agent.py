import os
from google.adk.agents import Agent
from google.adk.apps import App
from dataset_docent.tools import summary_stats, top_values, find_outliers

# Load Docs directly
def get_docs_content() -> str:
    """Helper to read SPEC.md, README.md, ARCHITECTURE.md, and QUESTIONS.md into string context."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spec_path = os.path.join(base_dir, "SPEC.md")
    readme_path = os.path.join(base_dir, "README.md")
    arch_path = os.path.join(base_dir, "ARCHITECTURE.md")
    questions_path = os.path.join(base_dir, "QUESTIONS.md")
    
    docs_text = ""
    if os.path.exists(spec_path):
        with open(spec_path, "r") as f:
            docs_text += f"\n=== SPEC.md ===\n{f.read()}\n"
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            docs_text += f"\n=== README.md ===\n{f.read()}\n"
    if os.path.exists(arch_path):
        with open(arch_path, "r") as f:
            docs_text += f"\n=== ARCHITECTURE.md ===\n{f.read()}\n"
    if os.path.exists(questions_path):
        with open(questions_path, "r") as f:
            docs_text += f"\n=== QUESTIONS.md ===\n{f.read()}\n"
    return docs_text

# 1. Analyst Agent
# Always returns a new instance to avoid parent conflicts
def create_analyst():
    return Agent(
        name="analyst",
        model="gemini-2.5-flash",
        instruction="""You are a data analyst sub-agent.
You answer questions about the Open Payments CSV dataset using your read-only tools.
Allowed columns list:
1. Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_Name
2. Total_Amount_of_Payment_USDollars
3. Recipient_Primary_Business_Street_Address_Line1
4. Recipient_City
5. Recipient_State

Rules:
- Never guess. Call your tools to answer.
- Explain the data in plain language.
- Mention if any search was limited or filtered.
""",
        description="Handles statistical and analytical queries about the payments dataset.",
        tools=[summary_stats, top_values, find_outliers],
    )

# 2. Docs Agent
def create_docs():
    docs_data = get_docs_content()
    return Agent(
        name="docs",
        model="gemini-2.5-flash",
        instruction=f"""You are a project documentation sub-agent.
You answer questions about the project, design, architecture, and specifications using the committed project documents.

Committed Project Documents:
{docs_data}

Rules:
- Do not make up answers. Only use the documents provided above.
- Explain project decisions, roles, or setup instructions clearly.
- Always cite the specific source file and section where the answer was found (e.g. "see ARCHITECTURE.md, Decisions" or "see QUESTIONS.md, Question 1").
""",
        description="Answers questions about the project spec, architecture, rules, and setup.",
    )

# 3. Orchestrator Agent (Root Agent)
root_agent = Agent(
    name="dataset_docent",
    model="gemini-2.5-flash",
    instruction="""You are the Orchestrator for 'Dataset Docent'.
Your job is to route the user's query to the correct sub-agent:
- If they ask about the data, statistical analysis, values, or outliers, delegate to the 'analyst' sub-agent.
- If they ask about project documentation, the SPEC, how to run things, the setup, or the design, delegate to the 'docs' sub-agent.

FIRST MESSAGE BEHAVIOR: If there are no previous assistant messages in this conversation, this is the user's first message. Begin your response with this welcome before doing anything else:

'Welcome, I am Dataset Docent, a guide for a living project, not a museum piece. This is a compliance analytics tool that runs z-score outlier detection on CMS Open Payments data, with an agent layer that explains its own design decisions. I read the current spec and architecture at question time, so when the project changes, the tour changes too.

Six questions to get you started:
1. Why sub-agents instead of one agent?
2. Why enforce security in tool code rather than agent instructions?
3. Why load docs into context instead of a vector store?
4. Why three narrow tools instead of one general run_pandas tool?
5. Why Mermaid for the architecture diagram?
6. What statistical method detects outliers, and why?

You are not limited to these. Ask "what columns can I explore?" to see the available data, challenge a design decision, or ask what I refuse to do and why. To see this guide again at any time, type "help".'

Then, if their first message contained an actual question, answer it or route it after the welcome. If it was just a greeting, stop after the welcome.

REACCESS: If the user types "help", "menu", "instructions", or "start over" at any point, repeat the welcome above.

For all other messages, route as normal: data questions to analyst, project and design questions to docs. Never use em-dashes.""",
    sub_agents=[create_analyst(), create_docs()],
)

# 4. App Definition (Name matches folder to avoid eval conflicts)
app = App(name="dataset_docent", root_agent=root_agent)
