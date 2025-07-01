import requests
import json
import os
from typing import Optional, Dict, Any

GRAPH_API_BASE = "https://graph.instagram.com"

def get_instagram_business_account(access_token):
    """
    Retrieves Instagram Business Account information using Facebook access token.
    Instagram Business API requires getting pages first, then finding linked IG accounts.
    
    Args:
        access_token (str): Facebook User access token
        
    Returns:
        dict: JSON response containing Instagram business account data
    """
    try:
        # First, get user's Facebook pages
        pages_url = "https://graph.facebook.com/v19.0/me/accounts"
        pages_params = {
            "access_token": access_token
        }
        pages_response = requests.get(pages_url, params=pages_params)
        print("Pages response:", pages_response.text)
        pages_response.raise_for_status()
        pages_data = pages_response.json()
        
        # Look for Instagram Business Account linked to each page
        for page in pages_data.get('data', []):
            page_id = page['id']
            page_token = page['access_token']
            
            # Check if this page has an Instagram Business Account
            ig_url = f"https://graph.facebook.com/v19.0/{page_id}"
            ig_params = {
                "fields": "instagram_business_account",
                "access_token": page_token
            }
            ig_response = requests.get(ig_url, params=ig_params)
            
            if ig_response.status_code == 200:
                ig_data = ig_response.json()
                ig_account = ig_data.get('instagram_business_account')
                
                if ig_account:
                    # Get detailed info about the Instagram account
                    ig_id = ig_account['id']
                    detail_url = f"https://graph.facebook.com/v19.0/{ig_id}"
                    detail_params = {
                        "fields": "id,username,name,profile_picture_url",
                        "access_token": page_token
                    }
                    detail_response = requests.get(detail_url, params=detail_params)
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        detail_data['page_access_token'] = page_token
                        detail_data['page_id'] = page_id
                        print("Instagram account found:", detail_data)
                        return detail_data
        
        # No Instagram Business Account found
        return {
            "error": "No Instagram Business Account found linked to your Facebook pages",
            "pages_found": len(pages_data.get('data', []))
        }
        
    except requests.exceptions.RequestException as e:
        print("Request error:", str(e))
        raise
    except Exception as e:
        print("General error:", str(e))
        raise

def post_to_instagram(message: str, access_token: str, ig_user_id: str, media_file=None) -> Dict[str, Any]:
    """
    Posts content to Instagram Business account with media attachment.
    
    Args:
        message (str): The text content to post (caption)
        access_token (str): Facebook page access token (not user token)
        ig_user_id (str): Instagram Business Account ID
        media_file: Uploaded file object (image or video)
        
    Returns:
        dict: Response containing success status and details
    """
    try:
        if media_file is None:
            return {
                "success": False,
                "message": "Instagram requires media (image or video) for all posts. Text-only posts are not supported.",
                "error": "Media required"
            }
        
        # Instagram Business API requires a publicly accessible URL, not direct file upload
        # We'll save the file locally and create a simple URL
        import tempfile
        import os
        import threading
        import http.server
        import socketserver
        from urllib.parse import quote
        
        # Save media file to a temporary location
        media_dir = "data/temp_media"
        os.makedirs(media_dir, exist_ok=True)
        
        # Create a unique filename
        import uuid
        file_extension = media_file.type.split('/')[-1]
        if file_extension == "jpeg":
            file_extension = "jpg"
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        temp_file_path = os.path.join(media_dir, unique_filename)
        
        # Save the file
        with open(temp_file_path, 'wb') as f:
            f.write(media_file.getvalue())
        
        try:
            # For development, we'll use a workaround with a public URL
            # In production, you'd upload to a CDN or cloud storage
            
            # Alternative approach: Upload to Facebook first to get a URL
            # This is a common workaround for Instagram Business API
            
            # Step 1: Upload to Facebook to get a hosted URL
            fb_upload_url = "https://graph.facebook.com/v19.0/me/photos"
            fb_upload_data = {
                'published': 'false',  # Don't publish to Facebook, just get URL
                'access_token': access_token
            }
            
            with open(temp_file_path, 'rb') as f:
                fb_files = {'source': (media_file.name, f, media_file.type)}
                print("Uploading media to Facebook for URL hosting...")
                fb_response = requests.post(fb_upload_url, data=fb_upload_data, files=fb_files)
            
            print(f"Facebook upload response: {fb_response.text}")
            
            if fb_response.status_code != 200:
                # Fallback: try using a placeholder image URL for testing
                return {
                    "success": False,
                    "message": "Failed to host media file. Instagram requires a publicly accessible URL.",
                    "error": f"Media hosting failed: {fb_response.text}"
                }
            
            fb_result = fb_response.json()
            
            # Get the photo URL from Facebook
            photo_id = fb_result.get('id')
            if not photo_id:
                return {
                    "success": False,
                    "message": "Failed to get media URL from Facebook hosting",
                    "error": "No photo ID returned"
                }
            
            # Get the actual image URL
            photo_url_response = requests.get(
                f"https://graph.facebook.com/v19.0/{photo_id}",
                params={
                    'fields': 'images',
                    'access_token': access_token
                }
            )
            
            if photo_url_response.status_code == 200:
                photo_data = photo_url_response.json()
                images = photo_data.get('images', [])
                if images:
                    # Use the highest resolution image
                    image_url = images[0]['source']
                else:
                    return {
                        "success": False,
                        "message": "Failed to get image URL from Facebook",
                        "error": "No image sources found"
                    }
            else:
                return {
                    "success": False,
                    "message": "Failed to retrieve image URL",
                    "error": photo_url_response.text
                }
            
            # Step 2: Create Instagram media container with the URL
            create_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
            
            # Determine media type
            media_type = "IMAGE" if media_file.type.startswith("image/") else "VIDEO"
            
            create_data = {
                'image_url' if media_type == "IMAGE" else 'video_url': image_url,
                'caption': message,
                'access_token': access_token
            }
            
            print(f"Creating Instagram media container with data: {create_data}")
            create_response = requests.post(create_url, data=create_data)
            
            print(f"Instagram create response: {create_response.text}")
            create_response.raise_for_status()
            creation_result = create_response.json()
            
            media_id = creation_result.get('id')
            if not media_id:
                return {
                    "success": False,
                    "message": f"Failed to create media container: {creation_result}",
                    "error": "No media ID returned"
                }
            
            # Step 2: Publish the media
            publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
            publish_data = {
                'creation_id': media_id,
                'access_token': access_token
            }
            
            print(f"Publishing Instagram media with data: {publish_data}")
            publish_response = requests.post(publish_url, data=publish_data)
            print(f"Instagram publish response: {publish_response.text}")
            publish_response.raise_for_status()
            result = publish_response.json()
            
            return {
                "success": True,
                "message": "Post published successfully to Instagram!",
                "post_id": result.get("id"),
                "response": result
            }
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
    except requests.exceptions.RequestException as e:
        error_detail = ""
        try:
            if hasattr(e, 'response') and e.response is not None:
                error_detail = f" - Response: {e.response.text}"
        except:
            pass
        
        return {
            "success": False,
            "message": f"Failed to post to Instagram: {str(e)}{error_detail}",
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "error": str(e)
        }

def load_instagram_credentials() -> Optional[Dict[str, Any]]:
    """
    Loads Instagram Business Account credentials with database-first, file-fallback approach.
    
    When USE_DATABASE is True:
    1. Try loading from database first
    2. If database fails or has no credentials, fall back to file storage
    
    When USE_DATABASE is False:
    1. Only try file storage
    
    Returns:
        dict or None: Instagram credentials if available, None otherwise
    """
    from app.config import USE_DATABASE
    
    try:
        if USE_DATABASE:
            # Try database first
            try:
                from app.db.database import execute_query
                query = "SELECT page_id, access_token, display_name FROM platform_accounts WHERE platform = 'instagram' LIMIT 1"
                result = execute_query(query, fetch=True)
                
                if result and len(result) > 0:
                    account_data = result[0]
                    print("✅ Instagram credentials loaded from database")
                    return {
                        "ig_user_id": account_data["page_id"],
                        "access_token": account_data["access_token"],
                        "username": account_data["display_name"]
                    }
                else:
                    print("💾 No Instagram credentials in database, trying file fallback...")
                    
            except Exception as e:
                print(f"⚠️  Database error, falling back to file: {e}")
            
            # Fallback to file if database failed or had no credentials
            secure_path = "app/secure/instagram_token.json"
            if os.path.exists(secure_path):
                try:
                    with open(secure_path, 'r') as f:
                        token_data = json.load(f)
                        if token_data.get("ig_user_id"):
                            print("✅ Instagram credentials loaded from file (fallback)")
                            return {
                                "ig_user_id": token_data.get("ig_user_id"),
                                "access_token": token_data.get("access_token"),
                                "username": token_data.get("username", "Instagram Account")
                            }
                except Exception as e:
                    print(f"Error reading Instagram file: {e}")
            
            print("❌ No Instagram credentials found in database or file")
            return None
        
        else:
            # Database disabled - only try file
            secure_path = "app/secure/instagram_token.json"
            if os.path.exists(secure_path):
                with open(secure_path, 'r') as f:
                    token_data = json.load(f)
                    if token_data.get("ig_user_id"):
                        print("✅ Instagram credentials loaded from file")
                        return {
                            "ig_user_id": token_data.get("ig_user_id"),
                            "access_token": token_data.get("access_token"),
                            "username": token_data.get("username", "Instagram Account")
                        }
            
            print("❌ No Instagram credentials found in file")
            return None
            
    except Exception as e:
        print(f"Error loading Instagram credentials: {e}")
        return None

def get_instagram_media(access_token: str, ig_user_id: str, limit: int = 25) -> Dict[str, Any]:
    """
    Retrieves recent media from Instagram Business Account.
    
    Args:
        access_token (str): Instagram User access token
        ig_user_id (str): Instagram Business Account ID
        limit (int): Number of media items to retrieve (default: 25)
        
    Returns:
        dict: Response containing media data or error information
    """
    try:
        url = f"{GRAPH_API_BASE}/{ig_user_id}/media"
        params = {
            "fields": "id,caption,media_type,media_url,thumbnail_url,timestamp,permalink",
            "limit": limit,
            "access_token": access_token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "media": result.get("data", []),
            "response": result
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"Failed to retrieve Instagram media: {str(e)}",
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "error": str(e)
        } 