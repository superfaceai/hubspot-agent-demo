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

## Test Results

| Test Case | Scenario | Composio Results | Superface Results |
|-----------|----------|-----------------|-------------------|
| **1. Create New Lead** | Create contact "John Doe" and company "ACME Ltd" when neither exists | ⚠️ **Partial Success**<br>✅ Created contact<br>✅ Associated contact with company<br>❌ Created two company records instead of one<br>❌ One company record lacked a name<br>❌ Other company incorrectly named "Acme Markets" | ✅ **Success**<br>✅ Created contact<br>✅ Created company<br>✅ Successfully associated contact with company |
| **2. Create New Lead with conflicts** | Create contact and company when both already exist but aren't associated | ⚠️ **Partial Success**<br>✅ No duplicate contact/company created<br>❌ Failed to create association between contact and company (5/5 attempts) | ⚠️ **Partial Success**<br>✅ No duplicate contact/company created<br>❌ Failed to create association between contact and company (2/5 attempts) |
| **3. Create New Deal** | Create a deal for existing contact and company | ❌ **Failure**<br>❌ Unable to create the deal due to association mapping errors | ✅ **Success**<br>✅ Created deal with proper associations<br>✅ Used default Sales pipeline and stage |
| **4. Create engagements** | Create call engagement and tasks based on call notes for existing deal | ❌ **Failure**<br>❌ Tools for creating engagements/tasks don't exist<br>❌ Agent couldn't use "Create new deal object" tool for this purpose | ✅ **Success**<br>✅ Created call engagement with notes<br>✅ Created tasks<br>✅ Properly associated with deal |
