import requests
import json
import os
from typing import Optional, Dict, Any

API_BASE_URL = "https://open-api.tiktok.com"

def get_user_info(access_token: str) -> Dict[str, Any]:
    """
    Retrieves basic user information from TikTok.
    
    Args:
        access_token (str): TikTok access token
        
    Returns:
        dict: JSON response containing user data
    """
    url = f"{API_BASE_URL}/user/info/"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    result = response.json()
    
    if 'data' not in result:
        raise ValueError(f"TikTok API error: {result}")
    
    return result['data']

def upload_video(access_token: str, video_file, caption: str = "", privacy_level: str = "SELF_ONLY") -> Dict[str, Any]:
    """
    Uploads a video to TikTok.
    
    Args:
        access_token (str): TikTok access token
        video_file: Video file object
        caption (str): Video caption/description
        privacy_level (str): Privacy setting - "SELF_ONLY", "MUTUAL_FOLLOW_FRIENDS", "FOLLOWER_OF_CREATOR", "PUBLIC_TO_EVERYONE"
        
    Returns:
        dict: Response containing success status and details
    """
    try:
        # Step 1: Initialize video upload
        init_url = f"{API_BASE_URL}/video/init/"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        init_data = {
            'post_info': {
                'title': caption,
                'privacy_level': privacy_level,
                'disable_duet': False,
                'disable_comment': False,
                'disable_stitch': False,
                'video_cover_timestamp_ms': 1000
            },
            'source_info': {
                'source': 'FILE_UPLOAD',
                'video_size': len(video_file.getvalue()),
                'chunk_size': 10000000,  # 10MB chunks
                'total_chunk_count': 1
            }
        }
        
        response = requests.post(init_url, json=init_data, headers=headers)
        response.raise_for_status()
        init_result = response.json()
        
        if 'data' not in init_result:
            raise ValueError(f"TikTok video init error: {init_result}")
        
        upload_url = init_result['data']['upload_url']
        publish_id = init_result['data']['publish_id']
        
        # Step 2: Upload video file
        video_file.seek(0)
        files = {'video': (video_file.name, video_file.getvalue(), 'video/mp4')}
        
        upload_response = requests.put(upload_url, files=files)
        upload_response.raise_for_status()
        
        # Step 3: Publish video
        publish_url = f"{API_BASE_URL}/video/publish/"
        publish_data = {
            'post_id': publish_id
        }
        
        publish_response = requests.post(publish_url, json=publish_data, headers=headers)
        publish_response.raise_for_status()
        publish_result = publish_response.json()
        
        if 'data' not in publish_result:
            raise ValueError(f"TikTok video publish error: {publish_result}")
        
        return {
            "success": True,
            "message": "Video uploaded successfully to TikTok!",
            "publish_id": publish_id,
            "response": publish_result
        }
        
    except requests.exceptions.RequestException as e:
        error_details = str(e)
        response_text = ""
        
        if hasattr(e, 'response') and e.response is not None:
            response_text = e.response.text
            print(f"TikTok API Error Response: {response_text}")
            
            try:
                error_json = e.response.json()
                if 'error' in error_json:
                    tiktok_error = error_json['error']
                    error_details = f"TikTok API Error: {tiktok_error.get('message', 'Unknown error')} (Code: {tiktok_error.get('code', 'N/A')})"
            except:
                error_details = f"TikTok API Error: {response_text}"
        
        return {
            "success": False,
            "message": f"Failed to upload video to TikTok: {error_details}",
            "error": error_details,
            "raw_response": response_text
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "error": str(e)
        }

def post_video_with_file(access_token: str, video_file, caption: str = "", privacy_level: str = "SELF_ONLY") -> Dict[str, Any]:
    """
    Posts a video to TikTok with the provided file.
    
    Args:
        access_token (str): TikTok access token
        video_file: Video file object
        caption (str): Video caption/description
        privacy_level (str): Privacy setting
        
    Returns:
        dict: Response containing success status and details
    """
    return upload_video(access_token, video_file, caption, privacy_level)

def load_tiktok_credentials() -> Optional[Dict[str, Any]]:
    """
    Loads TikTok credentials with database-first, file-fallback approach.
    
    When USE_DATABASE is True:
    1. Try loading from database first
    2. If database fails or has no credentials, fall back to file storage
    
    When USE_DATABASE is False:
    1. Only try file storage
    
    Returns:
        dict or None: TikTok credentials if available, None otherwise
    """
    from app.config import USE_DATABASE, TIKTOK_ACCESS_TOKEN
    
    try:
        # Check if we have a token from environment first
        if TIKTOK_ACCESS_TOKEN:
            print("✅ TikTok credentials loaded from environment")
            return {
                "access_token": TIKTOK_ACCESS_TOKEN,
                "open_id": "env_user",
                "display_name": "TikTok User"
            }
        
        if USE_DATABASE:
            # Try database first
            try:
                from app.db.database import execute_query
                query = "SELECT page_id, access_token, display_name FROM platform_accounts WHERE platform = 'tiktok' LIMIT 1"
                result = execute_query(query, fetch=True)
                
                if result and len(result) > 0:
                    account_data = result[0]
                    print("✅ TikTok credentials loaded from database")
                    return {
                        "access_token": account_data["access_token"],
                        "open_id": account_data["page_id"],
                        "display_name": account_data["display_name"]
                    }
                else:
                    print("💾 No TikTok credentials in database, trying file fallback...")
                    
            except Exception as e:
                print(f"⚠️  Database error, falling back to file: {e}")
            
            # Fallback to file if database failed or had no credentials
            secure_path = "app/secure/tiktok_token.json"
            if os.path.exists(secure_path):
                try:
                    with open(secure_path, 'r') as f:
                        token_data = json.load(f)
                        print("✅ TikTok credentials loaded from file (fallback)")
                        return {
                            "access_token": token_data["access_token"],
                            "open_id": token_data.get("open_id", "unknown"),
                            "display_name": token_data.get("display_name", "TikTok User")
                        }
                except Exception as e:
                    print(f"Error reading TikTok file: {e}")
            
            print("❌ No TikTok credentials found in database or file")
            return None
        
        else:
            # Database disabled - only try file
            secure_path = "app/secure/tiktok_token.json"
            if os.path.exists(secure_path):
                with open(secure_path, 'r') as f:
                    token_data = json.load(f)
                    print("✅ TikTok credentials loaded from file")
                    return {
                        "access_token": token_data["access_token"],
                        "open_id": token_data.get("open_id", "unknown"),
                        "display_name": token_data.get("display_name", "TikTok User")
                    }
            
            print("❌ No TikTok credentials found in file")
            return None
            
    except Exception as e:
        print(f"Error loading TikTok credentials: {e}")
        return None

def get_user_videos(access_token: str, cursor: int = 0, max_count: int = 20) -> Dict[str, Any]:
    """
    Retrieves user's TikTok videos.
    
    Args:
        access_token (str): TikTok access token
        cursor (int): Cursor for pagination
        max_count (int): Maximum number of videos to retrieve
        
    Returns:
        dict: JSON response containing video data
    """
    url = f"{API_BASE_URL}/video/list/"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'cursor': cursor,
        'max_count': max_count
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    result = response.json()
    
    if 'data' not in result:
        raise ValueError(f"TikTok API error: {result}")
    
    return result['data'] 