"""
X (Twitter) Authentication Module

This module handles OAuth 2.0 with PKCE authentication for X (Twitter) API v2.
X uses OAuth 2.0 Authorization Code Flow with PKCE for enhanced security.

Functions:
    - generate_x_auth_url(): Generate OAuth 2.0 authorization URL with PKCE
    - exchange_code_for_tokens(): Exchange authorization code for access/refresh tokens
    - refresh_access_token(): Refresh expired access token using refresh token
    - get_user_info(): Get authenticated user information
    - validate_access_token(): Validate current access token
    - save_x_credentials(): Save X credentials to database or file
    - load_x_credentials(): Load X credentials from database or file
"""

import os
import json
import base64
import hashlib
import secrets
import requests
from urllib.parse import urlencode, parse_qs
from app.config import (
    X_CLIENT_ID, X_CLIENT_SECRET, X_REDIRECT_URI,
    X_ACCESS_TOKEN, X_REFRESH_TOKEN, USE_DATABASE
)
from app.db.database import execute_query


def generate_code_verifier_and_challenge():
    """
    Generate PKCE code verifier and challenge for OAuth 2.0.
    
    Returns:
        tuple: (code_verifier, code_challenge) strings
    """
    # Generate a cryptographically random code verifier
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
    code_verifier = code_verifier.rstrip('=')  # Remove padding
    
    # Create code challenge using SHA256
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.rstrip('=')  # Remove padding
    
    return code_verifier, code_challenge


def generate_x_auth_url():
    """
    Generate X OAuth 2.0 authorization URL with PKCE.
    
    Returns:
        tuple: (auth_url, state, code_verifier) - Authorization URL, state parameter, and code verifier
    """
    if not X_CLIENT_ID:
        raise ValueError("X_CLIENT_ID not configured in environment variables")
    
    # Generate PKCE parameters
    code_verifier, code_challenge = generate_code_verifier_and_challenge()
    
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # X OAuth 2.0 scopes - requesting read/write permissions and offline access for refresh tokens
    # Note: media.write not needed as media uploads use OAuth 1.0a
    scopes = [
        'tweet.read',
        'tweet.write', 
        'users.read',
        'offline.access'   # Required for refresh tokens
    ]
    
    # OAuth 2.0 authorization parameters
    auth_params = {
        'response_type': 'code',
        'client_id': X_CLIENT_ID,
        'redirect_uri': X_REDIRECT_URI,
        'scope': ' '.join(scopes),
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    
    auth_url = f"https://x.com/i/oauth2/authorize?{urlencode(auth_params)}"
    
    return auth_url, state, code_verifier


def exchange_code_for_tokens(authorization_code, code_verifier, state=None):
    """
    Exchange authorization code for access and refresh tokens.
    
    Args:
        authorization_code (str): Authorization code from callback
        code_verifier (str): PKCE code verifier used in authorization
        state (str, optional): State parameter for validation
        
    Returns:
        dict: Token response containing access_token, refresh_token, etc.
    """
    if not X_CLIENT_ID or not X_CLIENT_SECRET:
        raise ValueError("X client credentials not configured")
    
    token_url = "https://api.x.com/2/oauth2/token"
    
    # Token exchange parameters
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': X_CLIENT_ID,
        'code': authorization_code,
        'redirect_uri': X_REDIRECT_URI,
        'code_verifier': code_verifier
    }
    
    # X requires client authentication via HTTP Basic Authentication
    # Encode client credentials as base64 for Authorization header
    credentials = f"{X_CLIENT_ID}:{X_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {encoded_credentials}'
    }
    
    try:
        response = requests.post(token_url, data=token_data, headers=headers)
        response.raise_for_status()
        
        token_info = response.json()
        
        # Validate required fields
        if 'access_token' not in token_info:
            raise ValueError("No access token in response")
        
        return token_info
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to exchange code for tokens: {str(e)}")


def refresh_access_token(refresh_token):
    """
    Refresh expired access token using refresh token.
    
    Args:
        refresh_token (str): Valid refresh token
        
    Returns:
        dict: New token response with fresh access_token
    """
    if not X_CLIENT_ID or not X_CLIENT_SECRET:
        raise ValueError("X client credentials not configured")
    
    token_url = "https://api.x.com/2/oauth2/token"
    
    refresh_data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': X_CLIENT_ID
    }
    
    # X requires client authentication via HTTP Basic Authentication
    # Encode client credentials as base64 for Authorization header
    credentials = f"{X_CLIENT_ID}:{X_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {encoded_credentials}'
    }
    
    try:
        response = requests.post(token_url, data=refresh_data, headers=headers)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to refresh access token: {str(e)}")


def get_user_info(access_token):
    """
    Get authenticated user information from X API.
    
    Args:
        access_token (str): Valid access token
        
    Returns:
        dict: User information including id, username, name, etc.
    """
    url = "https://api.x.com/2/users/me"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        user_data = response.json()
        
        if 'data' in user_data:
            return user_data['data']
        else:
            raise ValueError("Invalid user data response")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get user info: {str(e)}")


def validate_access_token(access_token):
    """
    Validate X access token by making a test API call.
    
    Args:
        access_token (str): Access token to validate
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        user_info = get_user_info(access_token)
        return user_info is not None and 'id' in user_info
    except:
        return False


def save_x_credentials(credentials):
    """
    Save X credentials to database or file based on configuration.
    
    Args:
        credentials (dict): Credentials containing access_token, refresh_token, etc.
    """
    if USE_DATABASE:
        # Save to database
        query = """
        INSERT INTO social_tokens (platform, access_token, refresh_token, user_id, username, expires_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        access_token = VALUES(access_token),
        refresh_token = VALUES(refresh_token),
        user_id = VALUES(user_id),
        username = VALUES(username),
        expires_at = VALUES(expires_at)
        """
        
        # Calculate expiration time (X tokens expire in 2 hours by default)
        import datetime
        expires_at = None
        if 'expires_in' in credentials:
            expires_at = datetime.datetime.now() + datetime.timedelta(seconds=credentials['expires_in'])
        
        execute_query(query, (
            'x',
            credentials.get('access_token'),
            credentials.get('refresh_token'),
            credentials.get('user_id'),
            credentials.get('username'),
            expires_at
        ))
    else:
        # Save to file
        credentials_dir = "data/credentials"
        os.makedirs(credentials_dir, exist_ok=True)
        
        credentials_file = os.path.join(credentials_dir, "x_credentials.json")
        
        with open(credentials_file, 'w') as f:
            json.dump(credentials, f, indent=2, default=str)


def load_x_credentials():
    """
    Load X credentials with database-first, file-fallback approach.
    
    When USE_DATABASE is True:
    1. Try loading from database first
    2. If database fails or has no credentials, fall back to file storage
    
    When USE_DATABASE is False:
    1. Only try file storage
    
    Returns:
        dict: Credentials dictionary or None if not found
    """
    if USE_DATABASE:
        # Try database first
        try:
            query = "SELECT * FROM social_tokens WHERE platform = 'x' ORDER BY created_at DESC LIMIT 1"
            result = execute_query(query, fetch=True)
            
            if result:
                row = result[0]
                print("✅ X credentials loaded from database")
                return {
                    'access_token': row[2],  # access_token column
                    'refresh_token': row[3],  # refresh_token column
                    'user_id': row[4],       # user_id column
                    'username': row[5],      # username column
                    'expires_at': row[6]     # expires_at column
                }
            else:
                print("💾 No X credentials in database, trying file fallback...")
                
        except Exception as e:
            print(f"⚠️  Database error, falling back to file: {e}")
        
        # Fallback to file if database failed or had no credentials
        credentials_file = "data/credentials/x_credentials.json"
        
        if os.path.exists(credentials_file):
            try:
                with open(credentials_file, 'r') as f:
                    credentials = json.load(f)
                    if credentials:
                        print("✅ X credentials loaded from file (fallback)")
                        return credentials
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading X file: {e}")
        
        print("❌ No X credentials found in database or file")
        return None
    
    else:
        # Database disabled - only try file
        credentials_file = "data/credentials/x_credentials.json"
        
        if os.path.exists(credentials_file):
            try:
                with open(credentials_file, 'r') as f:
                    credentials = json.load(f)
                    if credentials:
                        print("✅ X credentials loaded from file")
                        return credentials
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading X file: {e}")
        
        print("❌ No X credentials found in file")
        return None


def get_valid_access_token():
    """
    Get a valid access token, refreshing if necessary.
    
    Returns:
        str: Valid access token or None if unable to get one
    """
    # First try environment variable
    if X_ACCESS_TOKEN and validate_access_token(X_ACCESS_TOKEN):
        return X_ACCESS_TOKEN
    
    # Try stored credentials
    credentials = load_x_credentials()
    if not credentials:
        return None
    
    access_token = credentials.get('access_token')
    refresh_token = credentials.get('refresh_token')
    
    # Check if current token is still valid
    if access_token and validate_access_token(access_token):
        return access_token
    
    # Try to refresh the token
    if refresh_token:
        try:
            new_tokens = refresh_access_token(refresh_token)
            
            # Update stored credentials
            credentials.update(new_tokens)
            save_x_credentials(credentials)
            
            return new_tokens.get('access_token')
        except Exception as e:
            print(f"Failed to refresh X token: {e}")
    
    return None


if __name__ == "__main__":
    # Test authentication setup
    print("X Authentication Module")
    print("=" * 30)
    
    # Check configuration
    if not X_CLIENT_ID:
        print("❌ X_CLIENT_ID not configured")
    else:
        print("✅ X_CLIENT_ID configured")
    
    if not X_CLIENT_SECRET:
        print("❌ X_CLIENT_SECRET not configured")
    else:
        print("✅ X_CLIENT_SECRET configured")
    
    if not X_REDIRECT_URI:
        print("❌ X_REDIRECT_URI not configured")
    else:
        print("✅ X_REDIRECT_URI configured")
    
    # Test token validation
    token = get_valid_access_token()
    if token:
        print("✅ Valid X access token available")
        try:
            user_info = get_user_info(token)
            print(f"✅ Connected as: @{user_info.get('username', 'unknown')}")
        except Exception as e:
            print(f"❌ Error getting user info: {e}")
    else:
        print("❌ No valid X access token found")
        print("   Run 'python scripts/x_setup.py' to authenticate") 