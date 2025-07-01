"""
Pinterest API Platform Module

This module provides Pinterest API integration for the Social Media Scheduler.
It follows the same patterns as Facebook and Instagram platform modules.

Pinterest API v5 features:
- Pin creation with images
- Board management
- User account information
- Multi-platform batch posting compatibility
"""

import requests
import os
import tempfile
import json
from typing import Dict, Optional, List
import sys

# Add the project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.config import USE_DATABASE

# Pinterest API v5 endpoints
PINTEREST_API_BASE = "https://api.pinterest.com/v5"

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

def upload_media_to_pinterest(media_file, access_token: str) -> Dict:
    """
    Upload media to Pinterest and get media ID.
    
    Args:
        media_file: Uploaded media file object
        access_token (str): Pinterest access token
        
    Returns:
        Dict: Upload response with media_id
        
    Raises:
        Exception: If upload fails
    """
    if not media_file:
        raise Exception("No media file provided")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{media_file.name.split('.')[-1]}") as temp_file:
        temp_file.write(media_file.getvalue())
        temp_file_path = temp_file.name
    
    try:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        # Upload media file
        with open(temp_file_path, 'rb') as f:
            files = {
                'file': (media_file.name, f, media_file.type)
            }
            
            response = requests.post(
                f"{PINTEREST_API_BASE}/media",
                headers=headers,
                files=files
            )
            
        response.raise_for_status()
        upload_data = response.json()
        
        if "media_id" not in upload_data:
            raise Exception(f"No media_id in upload response: {upload_data}")
            
        return upload_data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Media upload failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Media upload error: {str(e)}")
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass

def get_user_boards(access_token: str) -> List[Dict]:
    """
    Get user's Pinterest boards.
    
    Args:
        access_token (str): Pinterest access token
        
    Returns:
        List[Dict]: List of user's boards
        
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
        return boards_data.get("items", [])
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get user boards: {str(e)}")
    except Exception as e:
        raise Exception(f"Boards retrieval error: {str(e)}")

def create_pin(access_token: str, board_id: str, title: str, description: str, media_id: Optional[str] = None, link: Optional[str] = None) -> Dict:
    """
    Create a pin on Pinterest.
    
    Args:
        access_token (str): Pinterest access token
        board_id (str): Target board ID
        title (str): Pin title
        description (str): Pin description
        media_id (str, optional): Media ID from upload
        link (str, optional): Link URL for the pin
        
    Returns:
        Dict: Pin creation response
        
    Raises:
        Exception: If pin creation fails
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Prepare pin data
    pin_data = {
        "board_id": board_id,
        "title": title[:100],  # Pinterest title limit
        "description": description[:800],  # Pinterest description limit
    }
    
    # Add media if provided
    if media_id:
        pin_data["media_source"] = {
            "source_type": "image_upload",
            "media_id": media_id
        }
    
    # Add link if provided
    if link:
        pin_data["link"] = link
    
    try:
        response = requests.post(
            f"{PINTEREST_API_BASE}/pins",
            headers=headers,
            json=pin_data
        )
        
        response.raise_for_status()
        pin_response = response.json()
        
        return pin_response
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Pin creation failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Pin creation error: {str(e)}")

def post_to_pinterest(message: str, access_token: str, user_id: str, media_file=None, board_id: Optional[str] = None) -> Dict:
    """
    Post content to Pinterest with multi-platform compatibility.
    
    Args:
        message (str): Post content (will be used as title and description)
        access_token (str): Pinterest access token
        user_id (str): Pinterest user ID
        media_file: Optional media file to upload
        board_id (str, optional): Specific board ID, uses default if not provided
        
    Returns:
        Dict: Standardised response for multi-platform integration
    """
    try:
        # Get user's boards if no board specified
        if not board_id:
            boards = get_user_boards(access_token)
            if not boards:
                return {
                    "success": False,
                    "message": "No boards found. Create a board first on Pinterest.",
                    "post_id": None
                }
            # Use the first board as default
            board_id = boards[0]["id"]
            board_name = boards[0]["name"]
        else:
            board_name = "Selected Board"
        
        # Split message into title and description
        lines = message.strip().split('\n', 1)
        title = lines[0][:100]  # Pinterest title limit
        description = message[:800]  # Pinterest description limit
        
        media_id = None
        
        # Upload media if provided
        if media_file:
            try:
                upload_response = upload_media_to_pinterest(media_file, access_token)
                media_id = upload_response["media_id"]
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Media upload failed: {str(e)}",
                    "post_id": None
                }
        
        # Create the pin
        pin_response = create_pin(
            access_token=access_token,
            board_id=board_id,
            title=title,
            description=description,
            media_id=media_id
        )
        
        pin_id = pin_response.get("id")
        
        if pin_id:
            return {
                "success": True,
                "message": f"Successfully posted to Pinterest board '{board_name}'",
                "post_id": pin_id,
                "platform_data": {
                    "board_id": board_id,
                    "board_name": board_name,
                    "pin_url": f"https://pinterest.com/pin/{pin_id}"
                }
            }
        else:
            return {
                "success": False,
                "message": "Pin created but no ID returned",
                "post_id": None
            }
            
    except Exception as e:
        error_message = str(e)
        
        # Handle specific Pinterest API errors
        if "401" in error_message:
            return {
                "success": False,
                "message": "Pinterest authentication failed. Please re-run pinterest_setup.py",
                "post_id": None
            }
        elif "403" in error_message:
            return {
                "success": False,
                "message": "Pinterest permission denied. Check your app permissions and scopes",
                "post_id": None
            }
        elif "429" in error_message:
            return {
                "success": False,
                "message": "Pinterest rate limit exceeded. Please try again later",
                "post_id": None
            }
        else:
            return {
                "success": False,
                "message": f"Pinterest posting failed: {error_message}",
                "post_id": None
            }

def get_pinterest_user_info(access_token: str) -> Dict:
    """
    Get Pinterest user account information.
    
    Args:
        access_token (str): Pinterest access token
        
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

def validate_pinterest_credentials(credentials: Dict) -> bool:
    """
    Validate Pinterest credentials by making a test API call.
    
    Args:
        credentials (Dict): Pinterest credentials to validate
        
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    try:
        access_token = credentials.get("access_token")
        if not access_token:
            return False
            
        # Test the credentials with a simple API call
        get_pinterest_user_info(access_token)
        return True
        
    except Exception:
        # Try to refresh token if available
        refresh_token = credentials.get("refresh_token")
        if refresh_token:
            try:
                from app.auth.pinterest_auth import refresh_access_token, save_pinterest_credentials
                new_tokens = refresh_access_token(refresh_token)
                # Update credentials with new tokens
                credentials.update(new_tokens)
                save_pinterest_credentials(credentials)
                return True
            except Exception:
                return False
        return False

def get_pinterest_boards_info(access_token: str) -> List[Dict]:
    """
    Get detailed information about user's Pinterest boards.
    
    Args:
        access_token (str): Pinterest access token
        
    Returns:
        List[Dict]: Detailed board information
    """
    try:
        boards = get_user_boards(access_token)
        
        # Format board information for display
        board_info = []
        for board in boards:
            board_info.append({
                "id": board.get("id", ""),
                "name": board.get("name", "Untitled Board"),
                "description": board.get("description", ""),
                "pin_count": board.get("pin_count", 0),
                "privacy": board.get("privacy", "public")
            })
        
        return board_info
        
    except Exception as e:
        print(f"Error getting Pinterest boards info: {str(e)}")
        return []

# Test function for development
def test_pinterest_connection():
    """
    Test Pinterest connection with stored credentials.
    For development and debugging purposes.
    """
    try:
        credentials = load_pinterest_credentials()
        if not credentials:
            print("❌ No Pinterest credentials found")
            return False
            
        if validate_pinterest_credentials(credentials):
            print("✅ Pinterest connection successful")
            
            # Get user info
            user_info = get_pinterest_user_info(credentials["access_token"])
            print(f"👤 User: {user_info.get('username', 'Unknown')}")
            
            # Get boards
            boards = get_pinterest_boards_info(credentials["access_token"])
            print(f"📌 Boards: {len(boards)} found")
            for board in boards[:3]:  # Show first 3 boards
                print(f"   - {board['name']} ({board['pin_count']} pins)")
            
            return True
        else:
            print("❌ Pinterest credentials validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Pinterest connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Run connection test when script is executed directly
    test_pinterest_connection() 
