import json
import re

def compare_tool_calls(expected_calls, actual_calls):
    """
    Compare expected tool calls with actual tool calls, allowing for flexible matching.
    
    Args:
        expected_calls (list): List of expected tool call dictionaries. Each call can include:
            - optional_tool_input_keys: List of keys that are optional in the input
            - optional: Boolean indicating if this tool call is optional
            - input_patterns: Dict of keys whose values should be matched as regexps
            - any_order: Boolean indicating if the order of this call is flexible
            - allow_additional_keys: Boolean indicating if additional keys are allowed in actual input
        actual_calls (list): List of actual tool call dictionaries
        
    Returns:
        tuple: (bool, str) - (success, reason)
    """
    # Track which actual calls have been matched
    remaining_actual_calls = actual_calls.copy()
    
    # First handle required calls, then optional ones
    required_calls = [call for call in expected_calls if not call.get('optional', False)]
    optional_calls = [call for call in expected_calls if call.get('optional', False)]
    
    if len(required_calls) > len(actual_calls):
        return False, f"Not enough actual calls to match required calls. Need {len(required_calls)}, got {len(actual_calls)}"
    
    for i, expected in enumerate(required_calls + optional_calls):
        is_optional = expected.get('optional', False)
        any_order = expected.get('any_order', False)
        allow_additional = expected.get('allow_additional_keys', False)
        input_patterns = expected.get('input_patterns', {})
        optional_keys = expected.get('optional_tool_input_keys', [])
        
        # Skip optional calls if no more actual calls available
        if is_optional and not any(call is not None for call in remaining_actual_calls):
            continue
            
        match_found = False
        for j, actual in enumerate(remaining_actual_calls):
            if actual is None:
                continue
                
            match_result = _match_tool_call(
                expected, 
                actual, 
                optional_keys=optional_keys,
                input_patterns=input_patterns,
                allow_additional=allow_additional
            )
            
            if match_result:
                match_found = True
                remaining_actual_calls[j] = None
                break
        
        if not match_found and not is_optional:
            # Include the function name in the error message for better debugging
            function_name = expected.get('tool_name', 'unknown')
            return False, f"No matching actual call found for {'optional' if is_optional else 'required'} call to function '{function_name}'"
    
    # Check if there are unmatched actual calls
    unmatched = [call for call in remaining_actual_calls if call is not None]
    
    return True, "All tool calls match"

def _match_tool_call(expected, actual, optional_keys=None, input_patterns=None, allow_additional=False):
    """Helper function to match a single tool call"""
    
    optional_keys = optional_keys or []
    input_patterns = input_patterns or {}
    
    # Check tool name
    if expected['tool_name'] != actual['tool_name']:
        return False
        
    # Check status
    if expected['tool_output']['status'] != actual['tool_output']['status']:
        return False
        
    expected_input = json.loads(expected['tool_input']) if isinstance(expected['tool_input'], str) else expected['tool_input']
    actual_input = json.loads(actual['tool_input']) if isinstance(actual['tool_input'], str) else actual['tool_input']
    
    # Check if non-optional keys exist
    required_keys = set(expected_input.keys()) - set(optional_keys)
    missing_keys = [key for key in required_keys if key not in actual_input]
    if missing_keys:
        return False
    
    # Check if there are unexpected keys (when not allowed)
    unexpected_keys = set(actual_input.keys()) - set(optional_keys) - set(expected_input.keys())
    if not allow_additional and unexpected_keys:
        return False
    
    # Check each expected key
    for key, expected_value in expected_input.items():
        # Skip optional keys not in actual input
        if key in optional_keys and key not in actual_input:
            continue
            
        if key not in actual_input:
            return False
            
        actual_value = actual_input[key]
        
        # Check if there are any deep patterns for this key
        deep_patterns = {k: v for k, v in input_patterns.items() if k.startswith(f"{key}.") or k.startswith(f"{key}[")}
        
        # If we have deep patterns for this key, use deep comparison
        if deep_patterns:
            pattern_dict = {}
            for pattern_key, pattern_value in deep_patterns.items():
                # Handle both dot notation (obj.prop) and array notation (obj[0])
                if pattern_key.startswith(f"{key}."):
                    # For dot notation: "associations.types.associationTypeId"
                    path = pattern_key.split(".", 1)[1]  # Remove the root key part
                elif pattern_key.startswith(f"{key}["):
                    # For array notation: "associations[0]"
                    path = pattern_key[len(key):]  # Remove the root key part
                else:
                    # Should not happen due to the filter above
                    continue
                    
                pattern_dict[path] = pattern_value
                
            if not _deep_compare(expected_value, actual_value, pattern_dict):
                return False
            
            continue
            
        # Simple pattern matching for string values
        if key in input_patterns:
            pattern = input_patterns[key]
            
            if pattern is None:
                # Skip pattern matching if pattern is None
                continue
                
            if not isinstance(actual_value, str):
                return False
                
            match = re.match(pattern, actual_value)
            
            if not match:
                return False
        # Regular value comparison
        elif expected_value != actual_value:
            return False
    
    return True

def _deep_compare(expected, actual, pattern_dict, current_path=""):
    """
    Recursively compare objects with support for regex patterns at specific paths.
    
    Args:
        expected: The expected value (can be dict, list, or primitive)
        actual: The actual value to compare against
        pattern_dict: Dictionary mapping paths to regex patterns
        current_path: Current path in the object hierarchy
        
    Returns:
        bool: True if objects match, False otherwise
    """
    # If types don't match, fail immediately (except for numeric types)
    if type(expected) != type(actual) and not (
        isinstance(expected, (int, float)) and isinstance(actual, (int, float))
    ):
        return False
        
    # Handle dictionaries
    if isinstance(expected, dict):
        # Check all expected keys exist in actual
        for key in expected:
            if key not in actual:
                return False
                
        # Recursively check each key
        for key in expected:
            new_path = f"{current_path}.{key}" if current_path else key
            if not _deep_compare(expected[key], actual[key], pattern_dict, new_path):
                return False
                
        return True
        
    # Handle lists
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            return False
            
        # Recursively check each item
        for i, (exp_item, act_item) in enumerate(zip(expected, actual)):
            new_path = f"{current_path}[{i}]"
            if not _deep_compare(exp_item, act_item, pattern_dict, new_path):
                return False
                
        return True
        
    # Handle primitive values
    else:
        # Check if we have a pattern for this path
        if current_path in pattern_dict:
            pattern = pattern_dict[current_path]
            
            # Skip if pattern is None
            if pattern is None:
                return True
                
            # For regex pattern matching, convert actual to string if needed
            actual_str = str(actual)
            match = re.match(pattern, actual_str)
            
            if not match:
                return False
                
            return True
        else:
            # Regular equality check
            if expected != actual:
                return False
                
            return True