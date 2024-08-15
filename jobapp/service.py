import requests

def fetch_location_data_from_api(api_url, api_token, limit=None, offset=None):
    headers = {
        'Authorization': f'Token {api_token}',
        'Accept': 'application/json',
    }
    
    # Append query parameters if provided
    params = {}
    if limit is not None:
        params['limit'] = limit
    if offset is not None:
        params['offset'] = offset
    
    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()