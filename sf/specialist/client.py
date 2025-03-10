from os import getenv
from typing import List

import requests
from requests.adapters import HTTPAdapter, Retry
from requests.models import Response

from superface.client import SuperfaceException, SuperfaceTool
from crewai.tools.structured_tool import CrewStructuredTool

# Add this line to define the environment variable with a default value
SUPERFACE_BASE_URL = getenv("SUPERFACE_BASE_URL", "https://superface.ai")

class SuperfaceSpecialist:
    @property
    def specialist_id(self):
        return self._specialist_id
        
    def __init__(self, api_key: str, specialist_id: str):
        if (not api_key):
            raise SuperfaceException("Please provide a valid API secret token")
        
        self._specialist_id = specialist_id
        
        self.api = SuperfaceSpecialistAPI(api_key=api_key, specialist_id=specialist_id)

    def get_tools(self, user_id: str) -> List[SuperfaceTool]:
        response_data = self.api.get(user_id=user_id, path='/')
        
        tools = []
        
        # If response_data is a dictionary (not a list of function descriptors)
        if isinstance(response_data, dict):
            # Create a single tool from the response data
            tool_name = response_data.get('name', self.api.specialist_id)
            
            def perform(arguments: dict | None, tool_name: str = tool_name):
                perform_path = f"/"
                data = arguments if arguments else dict()
                
                return self.api.post(user_id=user_id, path=perform_path, data=data)

            tool = SuperfaceTool(
                name=tool_name,
                description=response_data.get('description', ''),
                input=response_data.get('parameters', {}),
                is_safe=False,
                perform=perform
            )
            
            tools.append(tool)

        crewai_tools = []
        
        for superface_tool in tools:
            tool = CrewStructuredTool.from_function(
                name=superface_tool.name,
                description=superface_tool.description,
                args_schema=superface_tool.input_schema,
                func=lambda __sf_tool=superface_tool, **kwargs: __sf_tool.run(kwargs)
            )
            
            crewai_tools.append(tool)
        
        return crewai_tools

class SuperfaceSpecialistAPI:
    def __init__(self, *, 
                 api_key: str, 
                 specialist_id: str,
                 base_url: str = None):
        self.api_key = api_key
        
        # Safely combine URL parts
        if base_url is None:
            base_url = f"{SUPERFACE_BASE_URL.rstrip('/')}/api/specialists/"
            
        self.base_url = f"{base_url.rstrip('/')}/{specialist_id}"
        self.specialist_id = specialist_id

    def get(self, *, user_id: str, path: str):
        url = f"{self.base_url}{path}"

        s = requests.Session()

        retries = Retry(total=3,
                        backoff_factor=0.1,
                        status_forcelist=[ 500, 501, 502, 503, 504 ])

        s.mount('https://', HTTPAdapter(max_retries=retries))
        
        response = s.get(url, headers=self._get_headers(user_id))

        return self._handle_response(response)

    def post(self, *, user_id: str, path: str, data: dict):
        url = f"{self.base_url}{path}"
        
        response = requests.post(
            url,
            json=data,
            headers=self._get_headers(user_id)
        )

        return self._handle_response(response)
    
    def _handle_response(self, response: Response):
        if response.status_code >= 200 and response.status_code < 210:
            return response.json()
        elif response.status_code >=500:
            raise SuperfaceException("Something went wrong in the Superface")
        elif response.status_code == 400:
            raise SuperfaceException("Incorrect request")
        elif response.status_code == 401:
            raise SuperfaceException("Please provide a valid API token")
        elif response.status_code == 403:
            raise SuperfaceException("You don't have access to this resource")
        elif response.status_code == 404:
            raise SuperfaceException("Not found")
        elif response.status_code == 405:
            raise SuperfaceException("Something went wrong in the tool use. Please retry")
        else:
            raise SuperfaceException("Something went wrong in the agent")

    def _get_headers(self, user_id: str):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "x-superface-user-id": user_id,
            "Content-Type": "application/json"
        }