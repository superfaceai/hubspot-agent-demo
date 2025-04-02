# HubSpot Agent: Tools specialist vs API connectors

A comparative analysis of different CrewAI agent tool providers for automating HubSpot CRM operations. 

This repository serves as the foundation for comparing the performance of a tool specliast agent vs traditional API connectors. You can learn about agentic tool specialists at [Taking AI tool use to human level
](https://superface.ai/blog/introducing-specialists).

## Purpose

This repository compares the performance of CrewAI agents that interact with HubSpot CRM:
1. Using bre-built API connectors tools (via Composio)
2. Using Unified API, OAS mapped to tools (via Merge.dev)
3. Using [Superface Specialist](https://superface.ai/blog/introducing-specialists)

## Test Cases

All agent implementations use GPT-4o LLM for processing. Superface Specialist also uses GPT-4o internally for its operations.

<table border="1" cellspacing="0" cellpadding="5">
  <thead>
    <tr>
      <th>Test Case</th>
      <th>Scenario</th>
      <th>Prompt</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td valign="top"><strong>1. Create New Lead</strong></td>
      <td valign="top">Create contact "John Doe" and company "ACME Ltd" when neither exists</td>
      <td valign="top">Create a new lead, John Doe (john.doe@acme.com), and the company ACME Ltd (acme.com). Check for duplicate companies by name.</td>
    </tr>
    <tr>
      <td valign="top"><strong>2. Create New Lead with conflicts</strong></td>
      <td valign="top">Create contact and company when both already exist but aren't associated</td>
      <td valign="top">Create a new lead, John Doe (john.doe@acme.com), and the company ACME Ltd (acme.com). Check for duplicate companies by name.</td>
    </tr>
    <tr>
      <td valign="top"><strong>3. Create New Deal</strong></td>
      <td valign="top">Create a deal for existing contact and company</td>
      <td valign="top">Create a new deal for ACME ltd with John Doe as the contact.</td>
    </tr>
    <tr>
      <td valign="top"><strong>4. Create engagements</strong></td>
      <td valign="top">Create call engagement and tasks based on call notes for existing deal</td>
      <td valign="top">Create a call engagement and relevant tasks based on the call notes for the deal New Deal for ACME Ltd. This is the record from the call: Call with John Doe from ACME. Frustrated with manual sales processes, spreadsheets everywhere, and lack of automation. Using Pipedrive and HubSpot but not getting enough efficiency. Interested in lead scoring, follow-up automation, and reporting. Needs CFO approval, decision in 4–6 weeks, considering competitors but open to a pilot if we show quick value. Sending recap and confirming demo for March 15 at 2 PM EST, prepping the demo with a focus on automation and reporting, sending case studies, and following up in two weeks. Solid opportunity if we move fast.</td>
  </tbody>
</table>

## Test Results

<table border="1" cellspacing="0" cellpadding="5">
  <thead>
    <tr>
      <th>Test Case</th>
      <th>Composio</th>
      <th>Merge.dev</th>
      <th>Tools Specialist</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td valign="top"><strong>1. Create New Lead</strong></td>
      <td valign="top">
        ⚠️ <strong>Partial Success</strong><br>
        ✅ Created contact<br>
        ✅ Associated contact with company<br>
        ❌ Created two company records instead of one<br>
        ❌ One company record lacked a name<br>
        ❌ Other company incorrectly named "Acme Markets"
      </td>
      <td valign="top">
        ❌ <strong>Failure</strong><br>
        ❌ The operation to create a new lead for John Doe at ACME Ltd could not be completed as this action is not supported by the current integration.
      </td>
      <td valign="top">
        ✅ <strong>Success</strong><br>
        ✅ Created contact<br>
        ✅ Created company<br>
        ✅ Successfully associated contact with company
      </td>
    </tr>
    <tr>
      <td valign="top"><strong>2. Create New Lead with conflicts</strong></td>
      <td valign="top">
        ⚠️ <strong>Partial Success</strong><br>
        ✅ No duplicate contact/company created<br>
        ❌ Failed to create association between contact and company (5/5 attempts)
      </td>
      <td valign="top">
        ❌ <strong>Failure</strong><br>
        ❌ The operation to create a new lead for John Doe at ACME Ltd could not be completed as this action is not supported by the current integration.
      </td>
      <td valign="top">
        ⚠️ <strong>Partial Success</strong><br>
        ✅ No duplicate contact/company created<br>
        ❌ Failed to create association between contact and company (2/5 attempts)
      </td>
    </tr>
    <tr>
      <td valign="top"><strong>3. Create New Deal</strong></td>
      <td valign="top">
        ❌ <strong>Failure</strong><br>
        ❌ Unable to create the deal due to association mapping errors
      </td>
      <td valign="top">
        ❌ <strong>Failure</strong><br>
        ❌ Failed to create a new deal for ACME Ltd due to association errors and integration issues with the HubSpot API.
      </td>
      <td valign="top">
        ✅ <strong>Success</strong><br>
        ✅ Created deal with proper associations<br>
        ✅ Used default Sales pipeline and stage
      </td>
    </tr>
    <tr>
      <td valign="top"><strong>4. Create engagements</strong></td>
      <td valign="top">
        ❌ <strong>Failure</strong><br>
        ❌ Tools for creating engagements/tasks don't exist<br>
        ❌ Agent couldn't use "Create new deal object" tool for this purpose
      </td>
      <td valign="top">
        ❌ <strong>Failure</strong><br>
        ❌ Encountered issues creating call engagement and tasks<br>
        ❌ Invalid request formats and unrecognized company IDs<br>
        ❌ Unable to complete operations due to HubSpot API errors
      </td>
      <td valign="top">
        ✅ <strong>Success</strong><br>
        ✅ Created call engagement with notes<br>
        ✅ Created tasks<br>
        ✅ Properly associated with deal
      </td>
    </tr>
  </tbody>
</table>

### Prerequisites

- Python 3.11 or 3.12 installed

### Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example` with your API keys

4. Setup Composio account
   - Create and configure a Composio account
   - Connect your HubSpot account in Composio
   - Add these variables to your `.env` file:
     ```
     COMPOSIO_API_KEY=your_composio_api_key
     HUBSPOT_CONNECTED_ACCOUNT_ID=your_hubspot_account_id
     ```

5. Setup Merge.dev account
   - Create a Merge.dev account
   - Connect your HubSpot account in Merge.dev
   - Add these variables to your `.env` file:
     ```
     MERGE_API_KEY=your_merge_api_key
     MERGE_ACCOUNT_TOKEN=your_hubspot_account_id
     ```

6. Setup Superface account
   - Create a Superface account
   - Install the HubSpot Toolkit in Superface
   - Add this variable to your `.env` file:
     ```
     SUPERFACE_API_KEY=your_superface_api_key
     ```

7. OpenAI API key
   - Add your OpenAI API key to the `.env` file:
     ```
     OPENAI_API_KEY=your_openai_api_key
     ```

### Run the agents

You can run three different agent implementations with HubSpot connected tools:
1. CrewAI agent with Composio API connectors
   ```
   python composio/agent.py "your prompt here"
   ```
2. CrewAI agent with Superface Tools
   ```
   python sf/agent.py "your prompt here"
   ```
3. CrewAI agent with Superface Tools Specialist
   ```
   python sf/agent-specialist.py "your prompt here"
   ```
4. CrewAI agent with Merge.dev API connectors
   ```
   python merge/agent.py "your prompt here"
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
