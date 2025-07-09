import os
import requests
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
from urllib.parse import urlencode

# Test environment only
# Remove this in production
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# End test environment only

load_dotenv()

# Load environment variables
CLIENT_ID = os.getenv("TIKTOK_CLIENT_ID")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI")

AUTH_BASE_URL = "https://www.tiktok.com/auth/authorize/"
TOKEN_URL = "https://open-api.tiktok.com/oauth/access_token/"
SCOPES = ['user.info.basic', 'user.info.profile', 'video.list', 'video.upload', 'video.publish']

def get_tiktok_login_url():
    """
    Generate TikTok OAuth2 authorization URL.
    
    Returns:
        str: Authorization URL for TikTok login
    """
    params = {
        'client_key': CLIENT_ID,
        'scope': ','.join(SCOPES),
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'state': 'your_state_parameter'  # Should be random in production
    }
    
    auth_url = f"{AUTH_BASE_URL}?{urlencode(params)}"
    return auth_url

def fetch_tiktok_token(redirect_response_url):
    """
    Exchange authorization code for access token.
    
    Args:
        redirect_response_url (str): The full redirect URL containing the authorization code
        
    Returns:
        dict: Token response from TikTok API
    """
    from urllib.parse import urlparse, parse_qs
    
    # Parse authorization code from redirect URL
    parsed_url = urlparse(redirect_response_url)
    query_params = parse_qs(parsed_url.query)
    
    if 'code' not in query_params:
        raise ValueError("No authorization code found in redirect URL")
    
    auth_code = query_params['code'][0]
    
    # Exchange code for access token
    token_data = {
        'client_key': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(TOKEN_URL, data=token_data, headers=headers)
    response.raise_for_status()
    
    result = response.json()
    
    if 'data' not in result:
        raise ValueError(f"TikTok API error: {result}")
    
    return result['data'] 