import os
from google.adk.agents import Agent
from google.adk.apps import App
from app.tools import summary_stats, top_values, find_outliers

# Load Docs directly
def get_docs_content() -> str:
    """Helper to read SPEC.md, README.md, and ARCHITECTURE.md into string context."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spec_path = os.path.join(base_dir, "SPEC.md")
    readme_path = os.path.join(base_dir, "README.md")
    arch_path = os.path.join(base_dir, "ARCHITECTURE.md")
    
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
""",
        description="Answers questions about the project spec, architecture, rules, and setup.",
    )

# 3. Orchestrator Agent (Root Agent)
orchestrator = Agent(
    name="orchestrator",
    model="gemini-2.5-flash",
    instruction="""You are the Orchestrator for 'Dataset Docent'.
Your job is to route the user's query to the correct sub-agent:
- If they ask about the data, statistical analysis, values, or outliers, delegate to the 'analyst' sub-agent.
- If they ask about project documentation, the SPEC, how to run things, the setup, or the design, delegate to the 'docs' sub-agent.

Provide a friendly onboarding experience. If they ask generic onboarding or greetings, welcome them and describe your two sub-agents.
""",
    sub_agents=[create_analyst(), create_docs()],
)

# 4. App Definition (Name matches folder to avoid eval conflicts)
app = App(name="app", root_agent=orchestrator)
