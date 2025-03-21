import os
from dotenv import load_dotenv
from composio_crewai import ComposioToolSet, Action
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv(override=True)

# Initialize toolset
toolset = ComposioToolSet(api_key=os.getenv('COMPOSIO_API_KEY'))

if not os.getenv('HUBSPOT_CONNECTED_ACCOUNT_ID'):
    print("No connected account ID found!")
    exit()

connected_account_id = os.getenv('HUBSPOT_CONNECTED_ACCOUNT_ID')
print(f"Using connected account ID: {connected_account_id}")

# Set the connected account ID at the toolset level
toolset.connected_account_id = connected_account_id

# Get tools
tools = toolset.get_tools(
    actions=[Action.HUBSPOT_CREATE_CONTACT_OBJECT_WITH_PROPERTIES, 
             Action.HUBSPOT_CREATE_COMPANY_OBJECT, 
             Action.HUBSPOT_SEARCH_CONTACTS_BY_CRITERIA, 
             Action.HUBSPOT_SEARCH_COMPANY_OBJECTS,
             Action.HUBSPOT_CREATE_NEW_DEAL_OBJECT,
             Action.HUBSPOT_SEARCH_DEALS_BY_CRITERIA,
             Action.HUBSPOT_READ_PROPERTY_GROUPS_FOR_OBJECT_TYPE,
             Action.HUBSPOT_LIST_ASSOCIATION_TYPES,
             Action.HUBSPOT_CREATE_BATCH_OF_OBJECTS]
)

llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'), model="gpt-4o")

crewai_agent = Agent(
    role="HubSpot Agent",
    goal="You take action on HubSpot using HubSpot APIs",
    backstory="You are AI agent that is responsible for taking actions on HubSpot on behalf of users using HubSpot APIs",
    verbose=True,
    tools=tools,
    llm=llm,
)

task = Task(
    description=os.getenv("TEST_PROMPT"),
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