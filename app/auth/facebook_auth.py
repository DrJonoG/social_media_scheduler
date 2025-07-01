import os
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

# Test environment only
# Remove this in production
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# End test environment only

load_dotenv()

# Load environment variables
CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID")
CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET")
REDIRECT_URI = os.getenv("FACEBOOK_REDIRECT_URI")

AUTH_BASE_URL = "https://www.facebook.com/v19.0/dialog/oauth"
TOKEN_URL = "https://graph.facebook.com/v19.0/oauth/access_token"
SCOPES = ['pages_manage_posts', 'pages_read_engagement', 'pages_show_list', 'business_management']

def get_facebook_login_url():
    facebook = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    auth_url, _ = facebook.authorization_url(AUTH_BASE_URL)
    return auth_url

def fetch_facebook_token(redirect_response_url):
    facebook = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    token = facebook.fetch_token(
        TOKEN_URL,
        client_secret=CLIENT_SECRET,
        authorization_response=redirect_response_url
    )
    return token
