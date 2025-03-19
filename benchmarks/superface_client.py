from os import getenv, path
from typing import List
import os
from dotenv import load_dotenv

import requests
from requests.adapters import HTTPAdapter, Retry
from requests.models import Response

from superface.client import SuperfaceException

# Load environment variables from .env file
dotenv_path = path.join(path.dirname(path.dirname(path.abspath(__file__))), '.env')
if path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Define a default base URL
DEFAULT_BASE_URL = "https://pod.superface.ai"

def get_configuration_url(user_id: str):
    """
    Get the configuration URL for a given user_id by making a POST request to /api/hub/session
    
    Args:
        user_id (str): The user ID to get the configuration URL for
        
    Returns:
        str: The configuration URL
    """
    # Get API key and base URL from environment variables
    api_key = getenv('SUPERFACE_API_KEY')
    if not api_key:
        raise SuperfaceException("SUPERFACE_API_KEY environment variable is not set")
    
    base_url = getenv('SUPERFACE_BASE_URL', DEFAULT_BASE_URL).rstrip('/')
    
    # Create a SuperfaceAPI instance with the correct base URL
    api_base_url = f"{base_url}/api/hub"
    api = SuperfaceAPI(api_key=api_key, base_url=api_base_url)
    
    # Make the POST request to the session endpoint
    result = api.post(
        user_id=user_id,
        path="/session",
        data={}
    )
    
    # Extract and return the configuration URL from the response
    if 'configuration_url' in result:
        return result['configuration_url']
    else:
        raise SuperfaceException("Configuration URL not found in response")
    


class SuperfaceAPI:
    def __init__(self, *, 
                 api_key: str,
                 base_url: str = None):
        self.api_key = api_key
            
        self.base_url = base_url

    def get(self, *, user_id: str, path: str):
        url = f"{self.base_url}{path}"

        s = requests.Session()

        retries = Retry(total=3,
                        backoff_factor=0.1,
                        status_forcelist=[ 500, 501, 502, 503, 504 ])

        s.mount('https://', HTTPAdapter(max_retries=retries))
        
        response = s.get(url, headers=self._get_headers(user_id))

        return self._handle_response(response)

    def post(self, *, user_id: str, path: str, data: dict, override_base_url: str = None):
        """
        Make a POST request to the specified path
        
        Args:
            user_id (str): The user ID for the request
            path (str): The path to append to the base URL
            data (dict): The data to send in the request body
            override_base_url (str, optional): Override the base URL. Defaults to None.
            
        Returns:
            dict: The JSON response
        """
        if override_base_url:
            url = f"{override_base_url}{path}"
        else:
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
    
