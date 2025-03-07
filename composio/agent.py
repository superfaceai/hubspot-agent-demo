import os
from dotenv import load_dotenv
from composio_crewai import ComposioToolSet, App, Action
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Initialize toolset
toolset = ComposioToolSet(api_key=os.getenv('COMPOSIO_API_KEY'))

# Set up OAuth for HubSpot
# You'll need to get the HubSpot integration ID from Composio dashboard
hubspot_integration_id = os.getenv('HUBSPOT_INTEGRATION_ID')  # Add this to your .env file

# Get the integration details
integrations = toolset.get_integration(id=hubspot_integration_id)

# Handle the case where get_integration returns a list
if isinstance(integrations, list):
    # Find the right integration
    integration = None
    for integ in integrations:
        if getattr(integ, 'id', None) == hubspot_integration_id:
            integration = integ
            break
    
    if integration is None and integrations:
        # If not found by ID but list is not empty, use the first one
        integration = integrations[0]
        print(f"Using first available integration: {getattr(integration, 'id', 'unknown')}")
    
    if integration is None:
        print("No integration found!")
        exit()
else:
    # If it's already a single object
    integration = integrations

# For OAuth authentication with HubSpot
if not os.getenv('HUBSPOT_CONNECTED_ACCOUNT_ID'):
    print("No connected account ID found!")
    exit()

# If we have a connected account ID, use it to get tools
connected_account_id = os.getenv('HUBSPOT_CONNECTED_ACCOUNT_ID')
print(f"Using connected account ID: {connected_account_id}")

# Set the connected account ID at the toolset level
toolset.connected_account_id = connected_account_id

# Get tools without the connected_account_id parameter
tools = toolset.get_tools(
    actions=[Action.HUBSPOT_CREATE_CONTACT_OBJECT_WITH_PROPERTIES, Action.HUBSPOT_CREATE_COMPANY_OBJECT, Action.HUBSPOT_SEARCH_CONTACTS_BY_CRITERIA, Action.HUBSPOT_SEARCH_COMPANY_OBJECTS]
)

# Continue with your existing code
llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

crewai_agent = Agent(
    role="HubSpot Agent",
    goal="You take action on HubSpot using HubSpot APIs",
    backstory="You are AI agent that is responsible for taking actions on HubSpot on behalf of users using HubSpot APIs",
    verbose=True,
    tools=tools,
    llm=llm,
)

task = Task(
    description="Create new lead John Doe, john.doe@example.com, and company ACME ltd.",
    agent=crewai_agent,
    expected_output="Status of the operation"
)

crew = Crew(
    agents = [crewai_agent],
    tasks = [task]
)

# Replace crew.run() with crew.kickoff()
result = crew.kickoff()
print("\n\n=== RESULT ===")
print(result)