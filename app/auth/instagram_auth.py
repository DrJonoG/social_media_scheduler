import os
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Remove in production

load_dotenv()

CLIENT_ID = os.getenv("INSTAGRAM_CLIENT_ID")
CLIENT_SECRET = os.getenv("INSTAGRAM_CLIENT_SECRET")
REDIRECT_URI = os.getenv("INSTAGRAM_REDIRECT_URI")

AUTH_BASE_URL = "https://www.facebook.com/v19.0/dialog/oauth"
TOKEN_URL = "https://graph.facebook.com/v19.0/oauth/access_token"

SCOPES = [
    'instagram_basic',
    'instagram_content_publish',
    'pages_show_list',
    'pages_read_engagement',
    'pages_manage_posts'
]

def get_instagram_login_url():
    instagram = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    auth_url, _ = instagram.authorization_url(AUTH_BASE_URL)
    return auth_url

def fetch_instagram_token(redirect_response_url):
    instagram = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    token = instagram.fetch_token(
        TOKEN_URL,
        client_secret=CLIENT_SECRET,
        authorization_response=redirect_response_url
    )
    return token
