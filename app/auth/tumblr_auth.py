"""
Tumblr OAuth 1.0a Authentication Module

This module handles OAuth 1.0a authentication for Tumblr API access.
Unlike Facebook and Instagram which use OAuth 2.0, Tumblr uses OAuth 1.0a.
"""

import os
import json
import requests
import logging
from urllib.parse import urlencode, parse_qs
from requests_oauthlib import OAuth1Session
from app.config import USE_DATABASE

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tumblr OAuth 1.0a endpoints
TUMBLR_REQUEST_TOKEN_URL = "https://www.tumblr.com/oauth/request_token"
TUMBLR_AUTHORIZE_URL = "https://www.tumblr.com/oauth/authorize"
TUMBLR_ACCESS_TOKEN_URL = "https://www.tumblr.com/oauth/access_token"
TUMBLR_API_BASE_URL = "https://api.tumblr.com/v2"

def generate_tumblr_auth_url():
    """
    Generate the authorization URL for Tumblr OAuth 1.0a flow.
    
    Returns:
        dict: Contains auth_url, oauth_token, and oauth_token_secret
    """
    try:
        client_key = os.getenv('TUMBLR_CLIENT_ID')
        client_secret = os.getenv('TUMBLR_CLIENT_SECRET')
        callback_uri = os.getenv('TUMBLR_REDIRECT_URI')
        
        if not client_key or not client_secret:
            logger.error("Missing Tumblr client credentials")
            return None
        
        # Step 1: Get request token
        oauth = OAuth1Session(client_key, client_secret=client_secret, callback_uri=callback_uri)
        
        response = oauth.fetch_request_token(TUMBLR_REQUEST_TOKEN_URL)
        
        oauth_token = response['oauth_token']
        oauth_token_secret = response['oauth_token_secret']
        
        # Step 2: Generate authorization URL
        authorization_url = oauth.authorization_url(TUMBLR_AUTHORIZE_URL)
        
        return {
            'auth_url': authorization_url,
            'oauth_token': oauth_token,
            'oauth_token_secret': oauth_token_secret
        }
        
    except Exception as e:
        logger.error(f"Error generating Tumblr auth URL: {e}")
        return None

def exchange_code_for_tokens(oauth_token, oauth_token_secret, oauth_verifier):
    """
    Exchange OAuth verifier for access tokens.
    
    Args:
        oauth_token (str): OAuth token from request token step
        oauth_token_secret (str): OAuth token secret from request token step
        oauth_verifier (str): OAuth verifier from user authorization
        
    Returns:
        dict: Contains access_token, access_token_secret, and success status
    """
    try:
        client_key = os.getenv('TUMBLR_CLIENT_ID')
        client_secret = os.getenv('TUMBLR_CLIENT_SECRET')
        
        if not client_key or not client_secret:
            return {
                'success': False,
                'error': 'Missing Tumblr client credentials'
            }
        
        # Create OAuth session with request token
        oauth = OAuth1Session(
            client_key,
            client_secret=client_secret,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_token_secret,
            verifier=oauth_verifier
        )
        
        # Exchange for access token
        oauth_tokens = oauth.fetch_access_token(TUMBLR_ACCESS_TOKEN_URL)
        
        return {
            'success': True,
            'access_token': oauth_tokens['oauth_token'],
            'access_token_secret': oauth_tokens['oauth_token_secret']
        }
        
    except Exception as e:
        logger.error(f"Error exchanging Tumblr tokens: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_user_info(access_token, access_token_secret):
    """
    Get user information using access tokens.
    
    Args:
        access_token (str): OAuth access token
        access_token_secret (str): OAuth access token secret
        
    Returns:
        dict: User information or None if error
    """
    try:
        client_key = os.getenv('TUMBLR_CLIENT_ID')
        client_secret = os.getenv('TUMBLR_CLIENT_SECRET')
        
        oauth = OAuth1Session(
            client_key,
            client_secret=client_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        
        response = oauth.get(f"{TUMBLR_API_BASE_URL}/user/info")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('meta', {}).get('status') == 200:
                user_data = data.get('response', {}).get('user', {})
                blogs = user_data.get('blogs', [])
                
                # Get primary blog (or first blog)
                primary_blog = next((blog for blog in blogs if blog.get('primary')), blogs[0] if blogs else {})
                
                return {
                    'username': user_data.get('name', 'Unknown'),
                    'blog_name': primary_blog.get('name', ''),
                    'blog_title': primary_blog.get('title', ''),
                    'blog_url': primary_blog.get('url', ''),
                    'followers': primary_blog.get('followers', 0),
                    'following': user_data.get('following', 0),
                    'total_blogs': len(blogs),
                    'posts': primary_blog.get('posts', 0),
                    'blogs': blogs
                }
        
        logger.error(f"Failed to get user info: {response.status_code}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting Tumblr user info: {e}")
        return None

def validate_access_token(access_token, access_token_secret):
    """
    Validate access tokens by making a test API call.
    
    Args:
        access_token (str): OAuth access token
        access_token_secret (str): OAuth access token secret
        
    Returns:
        bool: True if tokens are valid, False otherwise
    """
    try:
        user_info = get_user_info(access_token, access_token_secret)
        return user_info is not None
    except Exception as e:
        logger.error(f"Error validating Tumblr tokens: {e}")
        return False

def save_tumblr_credentials(credentials, user_id=None):
    """
    Save Tumblr credentials to database or file.
    
    Args:
        credentials (dict): Credentials to save
        user_id (str, optional): User identifier for database storage
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        if USE_DATABASE:
            # Database storage using platform_accounts table
            from app.db.database import execute_query
            
            # Insert or update credentials in platform_accounts table
            query = """
            INSERT INTO platform_accounts (platform, page_id, access_token, access_token_secret, username, display_name)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            access_token = VALUES(access_token),
            access_token_secret = VALUES(access_token_secret),
            username = VALUES(username),
            display_name = VALUES(display_name),
            updated_at = CURRENT_TIMESTAMP
            """
            
            page_id = user_id or credentials.get('username', 'default')
            username = credentials.get('username', '')
            access_token = credentials.get('access_token', '')
            access_token_secret = credentials.get('access_token_secret', '')
            display_name = credentials.get('blog_title', username)
            
            execute_query(query, ('tumblr', page_id, access_token, access_token_secret, username, display_name))
            logger.info("Tumblr credentials saved to database")
            return True
        else:
            # File storage
            credentials_dir = "data/credentials"
            os.makedirs(credentials_dir, exist_ok=True)
            
            file_path = f"{credentials_dir}/tumblr_credentials.json"
            
            with open(file_path, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            logger.info("Tumblr credentials saved to file")
            return True
            
    except Exception as e:
        logger.error(f"Error saving Tumblr credentials: {e}")
        return False

def load_tumblr_credentials(user_id=None):
    """
    Load Tumblr credentials with database-first, file-fallback approach.
    
    When USE_DATABASE is True:
    1. Try loading from database first
    2. If database fails or has no credentials, fall back to file storage
    
    When USE_DATABASE is False:
    1. Only try file storage
    
    Args:
        user_id (str, optional): User identifier for database lookup
        
    Returns:
        dict: Credentials or None if not found
    """
    try:
        if USE_DATABASE:
            # Try database first
            try:
                from app.db.database import execute_query
                
                # Load credentials from platform_accounts table
                if user_id:
                    query = "SELECT access_token, access_token_secret, username, display_name FROM platform_accounts WHERE platform = 'tumblr' AND page_id = %s"
                    result = execute_query(query, (user_id,), fetch=True, dictionary=True)
                else:
                    query = "SELECT access_token, access_token_secret, username, display_name FROM platform_accounts WHERE platform = 'tumblr' LIMIT 1"
                    result = execute_query(query, fetch=True, dictionary=True)
                
                if result:
                    cred = result[0]
                    logger.info("✅ Tumblr credentials loaded from database")
                    return {
                        'access_token': cred['access_token'],
                        'access_token_secret': cred['access_token_secret'],
                        'username': cred.get('username', ''),
                        'blog_title': cred.get('display_name', '')
                    }
                else:
                    logger.info("💾 No Tumblr credentials in database, trying file fallback...")
                    
            except Exception as e:
                logger.warning(f"⚠️  Database error, falling back to file: {e}")
            
            # Fallback to file if database failed or had no credentials
            file_path = "data/credentials/tumblr_credentials.json"
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        credentials = json.load(f)
                        if credentials:
                            logger.info("✅ Tumblr credentials loaded from file (fallback)")
                            return credentials
                except Exception as e:
                    logger.error(f"Error reading Tumblr file: {e}")
            
            logger.info("❌ No Tumblr credentials found in database or file")
            return None
        
        else:
            # Database disabled - only try file
            file_path = "data/credentials/tumblr_credentials.json"
            
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    credentials = json.load(f)
                    if credentials:
                        logger.info("✅ Tumblr credentials loaded from file")
                        return credentials
            
            logger.info("❌ No Tumblr credentials found in file")
            return None
                
    except Exception as e:
        logger.error(f"Error loading Tumblr credentials: {e}")
        return None

def refresh_access_token(access_token, access_token_secret):
    """
    Tumblr OAuth 1.0a tokens don't expire, so this function just validates them.
    
    Args:
        access_token (str): Current access token
        access_token_secret (str): Current access token secret
        
    Returns:
        dict: Token validation result
    """
    try:
        if validate_access_token(access_token, access_token_secret):
            return {
                'success': True,
                'access_token': access_token,
                'access_token_secret': access_token_secret,
                'message': 'Tokens are still valid'
            }
        else:
            return {
                'success': False,
                'error': 'Tokens are invalid or expired'
            }
    except Exception as e:
        logger.error(f"Error validating Tumblr tokens: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_user_blogs(access_token, access_token_secret):
    """
    Get list of user's blogs.
    
    Args:
        access_token (str): OAuth access token
        access_token_secret (str): OAuth access token secret
        
    Returns:
        list: List of user's blogs
    """
    try:
        user_info = get_user_info(access_token, access_token_secret)
        if user_info:
            return user_info.get('blogs', [])
        return []
    except Exception as e:
        logger.error(f"Error getting user blogs: {e}")
        return []

# Utility functions for easier integration

def get_primary_blog_name(access_token, access_token_secret):
    """
    Get the primary blog name for posting.
    
    Args:
        access_token (str): OAuth access token
        access_token_secret (str): OAuth access token secret
        
    Returns:
        str: Primary blog name or None
    """
    try:
        user_info = get_user_info(access_token, access_token_secret)
        if user_info:
            return user_info.get('blog_name')
        return None
    except Exception as e:
        logger.error(f"Error getting primary blog name: {e}")
        return None

def test_tumblr_connection(user_id=None):
    """
    Test the Tumblr connection using stored credentials.
    
    Args:
        user_id (str, optional): User identifier for credential lookup
        
    Returns:
        dict: Connection test results
    """
    try:
        credentials = load_tumblr_credentials(user_id)
        if not credentials:
            return {
                'success': False,
                'error': 'No credentials found'
            }
        
        access_token = credentials.get('access_token')
        access_token_secret = credentials.get('access_token_secret')
        
        if not access_token or not access_token_secret:
            return {
                'success': False,
                'error': 'Invalid credentials format'
            }
        
        user_info = get_user_info(access_token, access_token_secret)
        if user_info:
            return {
                'success': True,
                'user_info': user_info,
                'message': f"Connected as @{user_info.get('username')} with {user_info.get('total_blogs', 0)} blog(s)"
            }
        else:
            return {
                'success': False,
                'error': 'Failed to retrieve user information'
            }
    except Exception as e:
        logger.error(f"Error testing Tumblr connection: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# Initialize database table if using database
def init_tumblr_db():
    """Initialize Tumblr tokens table in database."""
    if USE_DATABASE:
        try:
            from app.db.database import execute_query
            
            create_table_query = """
            CREATE TABLE IF NOT EXISTS tumblr_tokens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                access_token TEXT NOT NULL,
                access_token_secret TEXT NOT NULL,
                username VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            
            execute_query(create_table_query)
            logger.info("Tumblr tokens table initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Tumblr database: {e}")

# Initialize on import
if USE_DATABASE:
    init_tumblr_db() 