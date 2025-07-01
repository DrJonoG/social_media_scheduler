"""
Pinterest OAuth2 Authentication Module

This module handles Pinterest OAuth2 authentication flow for the Social Media Scheduler.
It follows the same patterns as Facebook and Instagram authentication modules.

Pinterest API v5 uses standard OAuth2 flow with:
- Authorization code flow
- Client ID and Client Secret
- Access tokens and refresh tokens
- Scopes for granular permissions
"""

import requests
import urllib.parse
import secrets
import base64
from typing import Dict, Optional, Tuple
import os
import sys

# Add the project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.config import (
    PINTEREST_CLIENT_ID, PINTEREST_CLIENT_SECRET, PINTEREST_REDIRECT_URI,
    USE_DATABASE
)

# Pinterest API v5 endpoints
PINTEREST_AUTH_URL = "https://www.pinterest.com/oauth/"
PINTEREST_TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
PINTEREST_API_BASE = "https://api.pinterest.com/v5"

# Pinterest OAuth2 scopes
PINTEREST_SCOPES = [
    "boards:read",
    "boards:write", 
    "pins:read",
    "pins:write",
    "user_accounts:read"
]

def generate_pinterest_auth_url() -> Tuple[str, str]:
    """
    Generate Pinterest OAuth2 authorization URL.
    
    Returns:
        Tuple[str, str]: (auth_url, state) - The authorization URL and state parameter
    """
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Build authorization URL parameters
    params = {
        "response_type": "code",
        "client_id": PINTEREST_CLIENT_ID,
        "redirect_uri": PINTEREST_REDIRECT_URI,
        "scope": ",".join(PINTEREST_SCOPES),
        "state": state
    }
    
    # Construct the full authorization URL
    auth_url = f"{PINTEREST_AUTH_URL}?{urllib.parse.urlencode(params)}"
    
    return auth_url, state

def exchange_code_for_tokens(auth_code: str) -> Dict:
    """
    Exchange authorization code for access tokens.
    
    Args:
        auth_code (str): Authorization code received from Pinterest
        
    Returns:
        Dict: Token response containing access_token, refresh_token, etc.
        
    Raises:
        Exception: If token exchange fails
    """
    # Prepare token exchange request
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64.b64encode(f'{PINTEREST_CLIENT_ID}:{PINTEREST_CLIENT_SECRET}'.encode()).decode()}"
    }
    
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": PINTEREST_REDIRECT_URI
    }
    
    try:
        response = requests.post(PINTEREST_TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        if "access_token" not in token_data:
            raise Exception(f"No access token in response: {token_data}")
            
        return token_data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to exchange code for tokens: {str(e)}")
    except Exception as e:
        raise Exception(f"Token exchange error: {str(e)}")

def refresh_access_token(refresh_token: str) -> Dict:
    """
    Refresh Pinterest access token using refresh token.
    
    Args:
        refresh_token (str): Valid refresh token
        
    Returns:
        Dict: New token response
        
    Raises:
        Exception: If token refresh fails
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64.b64encode(f'{PINTEREST_CLIENT_ID}:{PINTEREST_CLIENT_SECRET}'.encode()).decode()}"
    }
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    try:
        response = requests.post(PINTEREST_TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        if "access_token" not in token_data:
            raise Exception(f"No access token in refresh response: {token_data}")
            
        return token_data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to refresh token: {str(e)}")
    except Exception as e:
        raise Exception(f"Token refresh error: {str(e)}")

def get_user_info(access_token: str) -> Dict:
    """
    Get Pinterest user account information.
    
    Args:
        access_token (str): Valid Pinterest access token
        
    Returns:
        Dict: User account information
        
    Raises:
        Exception: If API request fails
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{PINTEREST_API_BASE}/user_account", headers=headers)
        response.raise_for_status()
        
        user_data = response.json()
        return user_data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get user info: {str(e)}")
    except Exception as e:
        raise Exception(f"User info error: {str(e)}")

def get_user_boards(access_token: str) -> Dict:
    """
    Get user's Pinterest boards.
    
    Args:
        access_token (str): Valid Pinterest access token
        
    Returns:
        Dict: User's boards information
        
    Raises:
        Exception: If API request fails
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{PINTEREST_API_BASE}/boards", headers=headers)
        response.raise_for_status()
        
        boards_data = response.json()
        return boards_data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get user boards: {str(e)}")
    except Exception as e:
        raise Exception(f"Boards retrieval error: {str(e)}")

def validate_access_token(access_token: str) -> bool:
    """
    Validate Pinterest access token by making a test API call.
    
    Args:
        access_token (str): Access token to validate
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        get_user_info(access_token)
        return True
    except Exception:
        return False

def save_pinterest_credentials(credentials: Dict) -> bool:
    """
    Save Pinterest credentials to database or file based on USE_DATABASE setting.
    
    Args:
        credentials (Dict): Pinterest credentials to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if USE_DATABASE:
            # Save to database
            from app.db.database import execute_query
            
            query = """
            INSERT INTO platform_accounts (platform, page_id, username, access_token, refresh_token, token_expires, additional_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            access_token = VALUES(access_token),
            refresh_token = VALUES(refresh_token),
            token_expires_at = VALUES(token_expires_at),
            additional_data = VALUES(additional_data),
            updated_at = CURRENT_TIMESTAMP
            """
            
            import json
            from datetime import datetime, timedelta
            
            # Calculate token expiry (Pinterest tokens typically last 1 year)
            expires_at = datetime.now() + timedelta(days=365)
            
            params = (
                "pinterest",
                credentials.get("user_id", ""),
                credentials.get("username", ""),
                credentials.get("access_token", ""),
                credentials.get("refresh_token", ""),
                expires_at,
                json.dumps({
                    "boards": credentials.get("boards", []),
                    "profile_image": credentials.get("profile_image", ""),
                    "account_type": credentials.get("account_type", "")
                })
            )
            
            execute_query(query, params)
            
        else:
            # Save to file
            import json
            import os
            
            secure_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "secure")
            os.makedirs(secure_dir, exist_ok=True)
            
            file_path = os.path.join(secure_dir, "pinterest_token.json")
            
            with open(file_path, 'w') as f:
                json.dump(credentials, f, indent=2, default=str)
        
        return True
        
    except Exception as e:
        print(f"Error saving Pinterest credentials: {str(e)}")
        return False

def load_pinterest_credentials() -> Optional[Dict]:
    """
    Load Pinterest credentials with database-first, file-fallback approach.
    
    When USE_DATABASE is True:
    1. Try loading from database first
    2. If database fails or has no credentials, fall back to file storage
    
    When USE_DATABASE is False:
    1. Only try file storage
    
    Returns:
        Optional[Dict]: Pinterest credentials if found, None otherwise
    """
    try:
        if USE_DATABASE:
            # Try database first
            try:
                from app.db.database import execute_query
                
                query = """
                SELECT page_id, username, access_token, refresh_token, token_expires, additional_data
                FROM platform_accounts
                WHERE platform = 'pinterest'
                ORDER BY updated_at DESC
                LIMIT 1
                """
                
                result = execute_query(query)
                
                if result:
                    import json
                    row = result[0]
                    additional_data = json.loads(row[5]) if row[5] else {}
                    
                    print("✅ Pinterest credentials loaded from database")
                    return {
                        "user_id": row[0],
                        "username": row[1],
                        "access_token": row[2],
                        "refresh_token": row[3],
                        "expires_at": row[4],
                        **additional_data
                    }
                else:
                    print("💾 No Pinterest credentials in database, trying file fallback...")
                    
            except Exception as e:
                print(f"⚠️  Database error, falling back to file: {e}")
            
            # Fallback to file if database failed or had no credentials
            import json
            import os
            
            file_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                "secure", 
                "pinterest_token.json"
            )
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        credentials = json.load(f)
                        if credentials:
                            print("✅ Pinterest credentials loaded from file (fallback)")
                            return credentials
                except Exception as e:
                    print(f"Error reading Pinterest file: {e}")
            
            print("❌ No Pinterest credentials found in database or file")
            return None
        
        else:
            # Database disabled - only try file
            import json
            import os
            
            file_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                "secure", 
                "pinterest_token.json"
            )
            
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    credentials = json.load(f)
                    if credentials:
                        print("✅ Pinterest credentials loaded from file")
                        return credentials
            
            print("❌ No Pinterest credentials found in file")
            return None
        
    except Exception as e:
        print(f"Error loading Pinterest credentials: {str(e)}")
        return None 
