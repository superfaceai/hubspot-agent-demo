import requests
import jsonref
import os
import json
from superface.client.schema_transformer import json_schema_to_pydantic
from crewai.tools.structured_tool import CrewStructuredTool
from dotenv import load_dotenv
load_dotenv()

MERGE_API_KEY = os.environ.get("MERGE_API_KEY", "")
MERGE_ACCOUNT_TOKEN = os.environ.get("MERGE_ACCOUNT_TOKEN", "")

def filter_x_merge(obj):
    if isinstance(obj, dict):
        return {k: filter_x_merge(v) for k, v in obj.items() if not k.startswith("x-merge")}
    elif isinstance(obj, list):
        return [filter_x_merge(item) for item in obj]
    else:
        return obj

def get_spec(openapi_spec_url):
    response = requests.get(openapi_spec_url)
    openapi_spec = response.json()
    cleaned_spec = jsonref.JsonRef.replace_refs(openapi_spec)
    cleaned_spec = filter_x_merge(cleaned_spec)
    return cleaned_spec

def make_api_call(category, path, method, input):
    headers = {"X-Account-Token": MERGE_ACCOUNT_TOKEN, "Authorization": f"Bearer {MERGE_API_KEY}"}

    url = f'https://api-eu.merge.dev/api/{category}/v1{path}'
    query_params = input.get('parameters', {})
    body = input.get('requestBody', None)

    if method.upper() == 'GET':
        response = requests.get(url, headers=headers, params=query_params)
    elif method.upper() == 'POST':
        response = requests.post(url, headers=headers, json=body, params=query_params)
    elif method.upper() == 'PUT':
        response = requests.put(url, headers=headers, json=body, params=query_params)
    elif method.upper() == 'DELETE':
        response = requests.delete(url, headers=headers, params=query_params)
    else:
        raise ValueError(f"HTTP method {method} not supported")

    return response.json()


def get_tools():
    category = "crm"
    spec = get_spec(f"https://api-eu.merge.dev/api/{category}/v1/schema")

    tools = []
    for path, methods in list(spec["paths"].items())[:]:
        for method, spec_with_ref in methods.items():
            function_name = spec_with_ref.get("operationId")
            description = spec_with_ref.get("description")
            parameters = spec_with_ref.get("parameters", [])
            request_body = (spec_with_ref.get("requestBody", {})
                        .get("content", {})
                        .get("application/json", {})
                        .get("schema"))

            schema = {"type": "object", "properties": {}}
            if request_body:
                filtered_req_body = {
                    k: v for k, v in request_body.get("properties", {}).items() if not k.startswith("x-merge")
                }
                json.dumps(filtered_req_body)
                schema["properties"]["requestBody"] = {
                    "type": "object",
                    "properties": filtered_req_body,
                }

            param_properties = {}
            for param in parameters:
                if "schema" in param and param["name"] != "X-Account-Token":
                    param_properties[param["name"]] = param["schema"]

            if param_properties:
                schema["properties"]["parameters"] = {
                    "type": "object",
                    "properties": param_properties,
                }

            # print(f"Function Name: {function_name}")
            # print(f"Description: {description}")
            # print(f"Path: {path}")
            # print(f"Method: {method}")
            # print(f"Parameters: {parameters}")
            # print(f"Request Body: {request_body}")
            # print(f"Schema: {schema}")
            # print("\n\n")
            
            tool = CrewStructuredTool.from_function(
                name=function_name,
                description=description,
                args_schema=json_schema_to_pydantic(schema),
                func=lambda _category=category, _path=path, _method=method, **kwargs: make_api_call(
                    category=_category,
                    path=_path,
                    method=_method,
                    input=kwargs
                ),
            )
            tools.append(tool)

    return tools