import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_location_data_from_api(api_url, api_token, **params):
    headers = {
        'Authorization': f'Token {api_token}',
        'Accept': 'application/json',
    }
    
    # Fetch data from the API with dynamic parameters
    response = requests.get(api_url, headers=headers, params=params)
    logger.info(f"Fetching data from API: {api_url} with params: {params}")
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()