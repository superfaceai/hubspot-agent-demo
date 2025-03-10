# HubSpot Agent Comparison

A comparative analysis of different CrewAI agent tool providers for automating HubSpot CRM operations.

## Purpose

This repository comapres CrewAI agents that interact with HubSpot CRM:
1. Using Composio tools
2. Using Superface Specialist

# Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example` with your API keys:
   ```
   COMPOSIO_API_KEY=your_composio_api_key
   OPENAI_API_KEY=your_openai_api_key
   HUBSPOT_CONNECTED_ACCOUNT_ID=your_hubspot_account_id
   TEST_PROMPT=your_TEST_PROMPT
   ```
4. Run the agent:
   ```
   python composio/agent.py
   ```

## Tests

### 1. Create New Lead

#### Test Scenario
- **Prompt:** "Create new lead John Doe, john.doe@acme.com, and company ACME Ltd, acme.com. Check for company duplicate by name."
- **Initial Conditions:** Neither the contact nor the company exist in HubSpot.

#### 1.1. Composio Results

✅ **Successes:**
- Created a contact
- Associated the contact with a company

❌ **Failures:**
- Created **two company records** instead of one
  - One company record **lacked a name**
  - The other was incorrectly named **Acme Markets**

#### 1.2. Superface Specialist Results

✅ **Successes:**
- Created a contact
- Created a company
- Successfully associated the contact with the company

❌ **Failures:**
*None*

### 2. Create New Lead with conflicts

#### Test Scenario
- **Prompt:** "Create new lead John Doe, john.doe@acme.com, and company ACME Ltd, acme.com. Check for company duplicate by name."
- **Initial Conditions:** Both contact and company already exist, but the association between the two does not.

#### 2.1. Composio Results

✅ **Successes:**
- No duplicate contact and company created

❌ **Failures:**
- Association between contact and company was not created 5/5 attempts

#### 2.2. Superface Specialist Results

✅ **Successes:**
- No duplicate contact and company created

❌ **Failures:**
- Association between contact and company was not created 2/5 attempts

### 3. Create New Deal

#### Test Scenario
- **Prompt:** "Create a new deal for ACME ltd with John Doe as the contact."
- **Initial Conditions:** Both contact and company already exist.

#### 3.1. Composio Results

✅ **Successes:**
*None*

❌ **Failures:**
- Unable to create the deal. There have been recurrent errors related to association mappings using HubSpot's tools, suggesting possible schema setup or categorical misunderstanding.

#### 3.2. Superface Specialist Results

✅ **Successes:**
- Creates a new deal and associations to the contact and company.
- Chooses default Sales pipeline and stage.

❌ **Failures:**
*None*

### 4. Create engagements

#### Test Scenario
- **Prompt:** "Create a call engagement and relevant tasks based on the call notes for the deal New Deal for ACME Ltd. This is the record from the call: Call with John Doe from ACME. Frustrated with manual sales processes, spreadsheets everywhere, and lack of automation. Using Pipedrive and HubSpot but not getting enough efficiency. Interested in lead scoring, follow-up automation, and reporting. Needs CFO approval, decision in 4–6 weeks, considering competitors but open to a pilot if we show quick value. Sending recap and confirming demo for March 15 at 2 PM EST, prepping the demo with a focus on automation and reporting, sending case studies, and following up in two weeks. Solid opportunity if we move fast."
- **Initial Conditions:** Deal already exist.

#### 4.1. Composio Results

✅ **Successes:**
*None*

❌ **Failures:**
- Tools for creating engagements or tasks does not exist. CrewAI agent was not able to use the **Create new deal object** tool to create the objects.

#### 4.2. Superface Specialist Results

✅ **Successes:**
- Creates a new call engagement with the call notes
- Creates tasks.
- Call engagement and tasks are correctly associated to the deal.

❌ **Failures:**
*None*

## Project Structure

- `composio/agent.py`: Main agent implementation using Composio and CrewAI
- `sf/agent.py`: Superface agent implementation
- `sf/agent-specialist.py`: Specialized Superface agent for HubSpot operations
- `sf/specialist/client.py`: Client implementation for the Superface specialist
- `.env.example`: Example environment variables file
- `requirements.txt`: Project dependencies