import json

def compare_tool_calls(expected_calls, actual_calls):
    """
    Compare expected tool calls with actual tool calls, allowing for flexible matching.
    
    Args:
        expected_calls (list): List of expected tool call dictionaries
        actual_calls (list): List of actual tool call dictionaries
        
    Returns:
        tuple: (bool, str) - (success, reason)
    """
    if len(expected_calls) != len(actual_calls):
        mismatch_reason = f"Tool call count mismatch: Expected {len(expected_calls)}, got {len(actual_calls)}"
        print(mismatch_reason)
        return False, mismatch_reason
    
    # Create a copy of actual calls that we can mark as matched
    remaining_actual_calls = actual_calls.copy()
    
    for i, expected in enumerate(expected_calls):
        print(f"\nChecking expected tool call {i+1}:")
        print(f"Expected: {json.dumps(expected, indent=2)}")
        
        expected_tool_name = expected['tool_name']
        expected_input = json.loads(expected['tool_input']) if isinstance(expected['tool_input'], str) else expected['tool_input']
        expected_status = expected['tool_output']['status']
        
        # Get optional keys if they exist
        optional_keys = expected.get('optional_tool_input_keys', [])
        print(f"Optional keys: {optional_keys}")
        
        # Find a matching actual call
        match_found = False
        matched_call_index = -1
        
        for j, actual in enumerate(remaining_actual_calls):
            if actual is None:  # Skip already matched calls
                continue
                
            actual_tool_name = actual['tool_name']
            actual_input = json.loads(actual['tool_input']) if isinstance(actual['tool_input'], str) else actual['tool_input']
            actual_status = actual['tool_output']['status']
            
            # Check if tool name matches
            if expected_tool_name != actual_tool_name:
                continue
                
            # Check if tool output status matches
            if expected_status != actual_status:
                continue
                
            # Check if all expected keys are in actual input
            keys_match = True
            for key, value in expected_input.items():
                # Skip checking optional keys if they're not in the actual input
                if key in optional_keys and key not in actual_input:
                    print(f"Skipping optional key: {key}")
                    continue
                    
                if key not in actual_input:
                    keys_match = False
                    break
                    
                # For values in angle brackets, just check that the actual value exists
                if isinstance(value, str) and value.startswith("<") and value.endswith(">"):
                    if actual_input[key] is None or actual_input[key] == "":
                        keys_match = False
                        break
                    print(f"Placeholder {value} matched with actual value {actual_input[key]}")
                # For regular values, check for exact match
                elif expected_input[key] != actual_input[key]:
                    keys_match = False
                    break
            
            if keys_match:
                match_found = True
                matched_call_index = j
                print(f"Matched with actual call: {json.dumps(actual, indent=2)}")
                if any(isinstance(value, str) and value.startswith("<") and value.endswith(">") for value in expected_input.values()):
                    print("Placeholder values were successfully matched")
                break
        
        if not match_found:
            mismatch_reason = f"No matching actual call found for expected call {i+1}"
            print(mismatch_reason)
            return False, mismatch_reason
        
        # Mark the matched call as used
        remaining_actual_calls[matched_call_index] = None
    
    print("All expected tool calls were matched!")
    return True, "All tool calls match" 