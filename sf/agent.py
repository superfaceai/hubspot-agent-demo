import os
import sys
from superface.crewai import Superface
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

prompt = sys.argv[1] if len(sys.argv) > 1 else os.getenv("TEST_PROMPT")
if not prompt:
    print("No prompt provided! Please provide a prompt as argument or set TEST_PROMPT environment variable.")
    exit()

superface = Superface(
    api_key=os.getenv("SUPERFACE_API_KEY")
)

# Get Superface tools
tools = superface.get_tools(
  user_id="user_123",
)

# Continue with your existing code
llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'), model="gpt-4o")

crewai_agent = Agent(
    role="HubSpot Agent",
    goal="You take action on HubSpot using HubSpot Tools",
    backstory="You are AI agent that is responsible for taking actions on HubSpot on behalf of users.",
    verbose=True,
    tools=tools,
    llm=llm,
)

task = Task(
    description=prompt,
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