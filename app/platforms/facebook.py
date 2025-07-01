import requests
import json
import os
from typing import Optional, Dict, Any

GRAPH_API_BASE = "https://graph.facebook.com/v19.0"

def get_user_pages(user_access_token):
    """
    Retrieves all Facebook pages associated with the user's access token.
    Tries both direct account access and business portfolio access.
    
    Args:
        user_access_token (str): User's Facebook access token
        
    Returns:
        dict: JSON response containing page data
    """
    # First try the standard method
    url = f"https://graph.facebook.com/v19.0/me/accounts"
    params = {
        "access_token": user_access_token
    }
    response = requests.get(url, params=params)
    print("Direct accounts response:", response.text)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('data'):
            return data
    
    # If no pages found via direct method, try business portfolio method
    print("No pages found via direct method, trying business portfolio...")
    try:
        # Get user's businesses
        business_url = f"https://graph.facebook.com/v19.0/me/businesses"
        business_response = requests.get(business_url, params=params)
        print("Business response:", business_response.text)
        
        if business_response.status_code == 200:
            business_data = business_response.json()
            all_pages = {"data": []}
            
            # For each business, get its pages
            for business in business_data.get('data', []):
                business_id = business['id']
                pages_url = f"https://graph.facebook.com/v19.0/{business_id}/client_pages"
                pages_response = requests.get(pages_url, params=params)
                print(f"Pages for business {business_id}:", pages_response.text)
                
                if pages_response.status_code == 200:
                    pages_data = pages_response.json()
                    # Add pages with access tokens
                    for page in pages_data.get('data', []):
                        # Get page access token
                        page_token_url = f"https://graph.facebook.com/v19.0/{page['id']}"
                        page_token_params = {
                            "fields": "access_token,name",
                            "access_token": user_access_token
                        }
                        token_response = requests.get(page_token_url, params=page_token_params)
                        if token_response.status_code == 200:
                            token_data = token_response.json()
                            page.update(token_data)
                            all_pages["data"].append(page)
            
            if all_pages["data"]:
                return all_pages
    
    except Exception as e:
        print(f"Error trying business portfolio method: {e}")
    
    # If both methods fail, raise the original response
    response.raise_for_status()
    return response.json()

def post_to_page(message, page_token, page_id):
    """
    Posts a text message to a specific Facebook page.
    
    Args:
        message (str): The text content to post
        page_token (str): Page access token
        page_id (str): Facebook page ID
        
    Returns:
        dict: JSON response from Facebook API
    """
    url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
    params = {
        "message": message,
        "access_token": page_token
    }
    response = requests.post(url, data=params)
    print("Response text:", response.text)  
    response.raise_for_status()
    return response.json()

def post_with_media_to_page(message: str, page_token: str, page_id: str, media_file=None) -> Dict[str, Any]:
    """
    Posts content to Facebook page with optional media attachment.
    
    Args:
        message (str): The text content to post
        page_token (str): Page access token
        page_id (str): Facebook page ID
        media_file: Uploaded file object (image or video)
        
    Returns:
        dict: Response containing success status and details
    """
    try:
        if media_file is not None:
            # Handle media upload
            url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
            
            # Reset file position to beginning if possible
            if hasattr(media_file, 'seek'):
                media_file.seek(0)
            
            # Get file content and ensure it's in bytes
            file_content = media_file.getvalue()
            if isinstance(file_content, str):
                file_content = file_content.encode('utf-8')
            
            # Determine proper content type
            content_type = getattr(media_file, 'type', 'image/jpeg')
            if not content_type or content_type == 'application/octet-stream':
                # Try to determine from filename
                filename = getattr(media_file, 'name', 'image.jpg')
                if filename.lower().endswith(('.png',)):
                    content_type = 'image/png'
                elif filename.lower().endswith(('.gif',)):
                    content_type = 'image/gif'
                elif filename.lower().endswith(('.webp',)):
                    content_type = 'image/webp'
                else:
                    content_type = 'image/jpeg'
            
            files = {
                'source': (
                    getattr(media_file, 'name', 'image.jpg'),
                    file_content,
                    content_type
                )
            }
            data = {
                'message': message,
                'access_token': page_token
            }
            
            response = requests.post(url, files=files, data=data)
        else:
            # Text-only post
            url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
            data = {
                "message": message,
                "access_token": page_token
            }
            response = requests.post(url, data=data)
        
        # Log the actual response for debugging
        print(f"Facebook API Response Status: {response.status_code}")
        print(f"Facebook API Response Headers: {response.headers}")
        print(f"Facebook API Response Text: {response.text}")
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "message": "Post published successfully to Facebook!",
            "post_id": result.get("id"),
            "response": result
        }
        
    except requests.exceptions.RequestException as e:
        # Capture detailed error information
        error_details = str(e)
        response_text = ""
        
        if hasattr(e, 'response') and e.response is not None:
            response_text = e.response.text
            print(f"Facebook API Error Response: {response_text}")
            
            try:
                error_json = e.response.json()
                if 'error' in error_json:
                    fb_error = error_json['error']
                    error_details = f"Facebook API Error: {fb_error.get('message', 'Unknown error')} (Code: {fb_error.get('code', 'N/A')}, Type: {fb_error.get('type', 'N/A')})"
            except:
                error_details = f"Facebook API Error: {response_text}"
        
        return {
            "success": False,
            "message": f"Failed to post to Facebook: {error_details}",
            "error": error_details,
            "raw_response": response_text
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "error": str(e)
        }

def load_facebook_credentials() -> Optional[Dict[str, Any]]:
    """
    Loads Facebook page credentials with database-first, file-fallback approach.
    
    When USE_DATABASE is True:
    1. Try loading from database first
    2. If database fails or has no credentials, fall back to file storage
    
    When USE_DATABASE is False:
    1. Only try file storage
    
    Returns:
        dict or None: Page credentials if available, None otherwise
    """
    from app.config import USE_DATABASE
    
    try:
        if USE_DATABASE:
            # Try database first
            try:
                from app.db.database import execute_query
                query = "SELECT page_id, access_token, display_name FROM platform_accounts WHERE platform = 'facebook' LIMIT 1"
                result = execute_query(query, fetch=True)
                
                if result and len(result) > 0:
                    page_data = result[0]
                    print("✅ Facebook credentials loaded from database")
                    return {
                        "page_id": page_data["page_id"],
                        "page_token": page_data["access_token"],
                        "page_name": page_data["display_name"]
                    }
                else:
                    print("💾 No Facebook credentials in database, trying file fallback...")
                    
            except Exception as e:
                print(f"⚠️  Database error, falling back to file: {e}")
            
            # Fallback to file if database failed or had no credentials
            secure_path = "app/secure/facebook_token.json"
            if os.path.exists(secure_path):
                try:
                    with open(secure_path, 'r') as f:
                        token_data = json.load(f)
                        if token_data.get("data") and len(token_data["data"]) > 0:
                            # Return the first page's credentials
                            first_page = token_data["data"][0]
                            print("✅ Facebook credentials loaded from file (fallback)")
                            return {
                                "page_id": first_page["id"],
                                "page_token": first_page["access_token"],
                                "page_name": first_page.get("name", "Unknown Page")
                            }
                except Exception as e:
                    print(f"Error reading Facebook file: {e}")
            
            print("❌ No Facebook credentials found in database or file")
            return None
        
        else:
            # Database disabled - only try file
            secure_path = "app/secure/facebook_token.json"
            if os.path.exists(secure_path):
                with open(secure_path, 'r') as f:
                    token_data = json.load(f)
                    if token_data.get("data") and len(token_data["data"]) > 0:
                        # Return the first page's credentials
                        first_page = token_data["data"][0]
                        print("✅ Facebook credentials loaded from file")
                        return {
                            "page_id": first_page["id"],
                            "page_token": first_page["access_token"],
                            "page_name": first_page.get("name", "Unknown Page")
                        }
            
            print("❌ No Facebook credentials found in file")
            return None
            
    except Exception as e:
        print(f"Error loading Facebook credentials: {e}")
        return None

def update_page_profile_picture(page_token: str, page_id: str, image_file) -> Dict[str, Any]:
    """
    Updates the profile picture of a Facebook page.
    
    Args:
        page_token (str): Page access token
        page_id (str): Facebook page ID
        image_file: Uploaded image file object
        
    Returns:
        dict: Response containing success status and details
    """
    try:
        url = f"https://graph.facebook.com/v19.0/{page_id}/picture"
        files = {
            'source': (image_file.name, image_file.getvalue(), image_file.type)
        }
        data = {
            'access_token': page_token
        }
        
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "message": "Profile picture updated successfully!",
            "response": result
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"Failed to update profile picture: {str(e)}",
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "error": str(e)
        }


def update_page_cover_photo(page_token: str, page_id: str, image_file) -> Dict[str, Any]:
    """
    Updates the cover photo of a Facebook page.
    
    Args:
        page_token (str): Page access token
        page_id (str): Facebook page ID
        image_file: Uploaded image file object
        
    Returns:
        dict: Response containing success status and details
    """
    try:
        # First, upload the photo to get a photo ID
        upload_url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
        files = {
            'source': (image_file.name, image_file.getvalue(), image_file.type)
        }
        upload_data = {
            'published': 'false',  # Don't publish to timeline
            'access_token': page_token
        }
        
        upload_response = requests.post(upload_url, files=files, data=upload_data)
        upload_response.raise_for_status()
        upload_result = upload_response.json()
        
        photo_id = upload_result.get('id')
        if not photo_id:
            return {
                "success": False,
                "message": "Failed to upload cover photo - no photo ID returned",
                "error": "No photo ID in response"
            }
        
        # Now set the uploaded photo as the cover
        cover_url = f"https://graph.facebook.com/v19.0/{page_id}"
        cover_data = {
            'cover': photo_id,
            'access_token': page_token
        }
        
        cover_response = requests.post(cover_url, data=cover_data)
        cover_response.raise_for_status()
        cover_result = cover_response.json()
        
        return {
            "success": True,
            "message": "Cover photo updated successfully!",
            "photo_id": photo_id,
            "response": cover_result
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"Failed to update cover photo: {str(e)}",
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "error": str(e)
        }