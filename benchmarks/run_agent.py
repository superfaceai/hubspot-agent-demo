import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union
import json
import re
from pydantic import BaseModel
import enum
from datetime import datetime

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sf.specialist.client import SuperfaceSpecialist
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

from superface.client import Superface

def run(prompt: str, specialist_id: str = "hubspot", user_id: str = "user_123", model: str = "gpt-4o", temperature: float = 0.1, seed: int = 42):
    """
    Run a specialist agent with the provided prompt and return the result.
    
    Args:
        prompt: The prompt to send to the agent
        specialist_id: The ID of the specialist to use (default: "hubspot")
        user_id: The user ID to use for tool connections (default: "user_123")
        model: The LLM model to use (default: "gpt-4o")
        temperature: The temperature setting for the LLM (default: 0.1)
        seed: The random seed for the LLM (default: 42)
        
    Returns:
        A dictionary containing the result and tool calls
    """
    # Initialize the specialist
    specialist = SuperfaceSpecialist(
        api_key=os.getenv("SUPERFACE_API_KEY"),
        specialist_id=specialist_id
    )
    
    # Get Superface Specialist tools
    tools = specialist.get_tools(
        user_id=user_id,
    )
    
    # Initialize the LLM
    llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'), model=model, temperature=temperature, seed=seed)
    
    # Create the agent
    crewai_agent = Agent(
        role=f"{specialist_id.capitalize()} Agent",
        goal=f"You take action on {specialist_id.capitalize()} using {specialist_id.capitalize()} Specialist.",
        backstory=f"You should delegate tasks to {specialist_id.capitalize()} Specialist to take actions on {specialist_id.capitalize()} on behalf of users. In case that the specialist returns action required error and requires configure access provide the action url to the user.",
        verbose=True,
        tools=tools,
        llm=llm,
    )
    
    # Define the JSON schema for expected output
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["success", "error", "completed"]
            },
            "details": {
                "type": "string"
            },
            "executions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string"
                        },
                        "groupId": {
                            "type": "string"
                        },
                        "toolCall": {
                            "type": "object",
                            "properties": {
                                "kind": {
                                    "type": "string"
                                },
                                "id": {
                                    "type": "string"
                                },
                                "groupId": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "arguments": {
                                    "type": "string"
                                }
                            },
                            "required": ["kind", "name", "arguments"]
                        },
                        "status": {
                            "type": "string",
                            "enum": ["completed", "error"]
                        },
                        "result": {
                            "type": "object"
                        }
                    },
                    "required": ["toolCall", "status"]
                }
            }
        },
        "required": ["status", "details", "executions"]
    }
    
    # Create the task with proper output format specification
    task = Task(
        description=prompt,
        agent=crewai_agent,
        expected_output=f"JSON object matching following schema: {json.dumps(json_schema, indent=2)}. Always include the executions array with all tool calls made.",
    )
    
    # Create and run the crew
    crew = Crew(
        agents=[crewai_agent],
        tasks=[task]
    )
    
    # Run the crew
    result = crew.kickoff()
    
    # Extract tool calls from the result
    tool_calls = []

    try:
        # First, try to clean up the raw output by removing markdown formatting
        cleaned_raw = result.raw
        
        # Extract content between JSON code blocks if present
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', cleaned_raw)
        if json_match:
            cleaned_raw = json_match.group(1).strip()
        
        # Remove any trailing backticks that might have been missed
        cleaned_raw = cleaned_raw.rstrip('`')
        
        # Replace Python literals with JSON equivalents
        cleaned_raw = (cleaned_raw
            .replace('False', 'false')
            .replace('True', 'true')
            .replace('None', 'null'))
        
        # Try to parse the JSON
        try:
            agent_response = json.loads(cleaned_raw)
            
            # Extract tool calls from executions
            if isinstance(agent_response, dict) and 'executions' in agent_response:
                for execution in agent_response['executions']:
                    if isinstance(execution, dict) and 'toolCall' in execution:
                        tool_call = execution['toolCall']
                        formatted_tool_call = {
                            'tool_name': tool_call.get('name', ''),
                            'tool_input': tool_call.get('arguments', '{}'),
                            'tool_output': {
                                'status': execution.get('status', 'unknown')
                            }
                        }
                        tool_calls.append(formatted_tool_call)
        except json.JSONDecodeError as e:
            print(f"Error parsing cleaned JSON: {str(e)}")
            
            # Fallback: Use regex to extract tool calls directly
            tool_call_pattern = r'"name"\s*:\s*"([^"]+)".*?"arguments"\s*:\s*"({[^}]+})".*?"status"\s*:\s*"([^"]+)"'
            matches = re.findall(tool_call_pattern, cleaned_raw, re.DOTALL)
            
            for tool_name, tool_input, status in matches:
                # Clean up escaped quotes in the tool input
                tool_input = tool_input.replace('\\"', '"')
                formatted_tool_call = {
                    'tool_name': tool_name,
                    'tool_input': tool_input,
                    'tool_output': {
                        'status': status
                    }
                }
                tool_calls.append(formatted_tool_call)
                
    except Exception as e:
        print(f"Error extracting tool calls: {str(e)}")
    
    return {
        "result": str(result),
        "tool_calls": tool_calls
    }