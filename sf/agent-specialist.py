import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import directly from the local directory
from sf.specialist.client import SuperfaceSpecialist
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# Create a different approach to importing
try:
    # Try the package-style import first
    from sf.specialist.client import SuperfaceSpecialist
except ModuleNotFoundError:
    # If that fails, try a direct relative import
    from specialist.client import SuperfaceSpecialist

# Rename the variable to avoid collision with the package name
specialist = SuperfaceSpecialist(
    api_key=os.getenv("SUPERFACE_API_KEY"),
    specialist_id="hubspot"
)

# Get Superface Specialist tools
tools = specialist.get_tools(
  user_id="user_123",
)

# Continue with your existing code
llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'), model="gpt-4o")

crewai_agent = Agent(
    role="HubSpot Agent",
    goal="You take action on HubSpot using HubSpot Specialist",
    backstory="You are AI agent that is responsible for taking actions on HubSpot on behalf of users.",
    verbose=True,
    tools=tools,
    llm=llm,
)

task = Task(
    description="Create new lead John Doe, john.doe@example.com, and company ACME ltd, check for company duplicate by name.",
    agent=crewai_agent,
    expected_output="Status of the operation"
)

crew = Crew(
    agents = [crewai_agent],
    tasks = [task]
)

# Run the crew
result = crew.kickoff()
print("\n\n=== RESULT ===")
print(result)