"""
X (Twitter) Platform Integration

This module handles posting to X (Twitter) using a hybrid OAuth approach.
Supports text posts, media posts (images/videos), and scheduled posting.

Key Features:
- Text-only tweets
- Image and video uploads with tweets
- Proper error handling and response formatting
- Hybrid authentication: OAuth 1.0a for media upload + OAuth 2.0 for tweets
- Media upload via v1.1 API (OAuth 1.0a required)
- Tweet posting via v2 API (OAuth 2.0)
- Multi-platform integration compatibility

Functions:
    - post_to_x(): Main posting function for multi-platform integration
    - create_x_post(): Core tweet creation with media support
    - upload_media_to_x(): Upload media files to X using v1.1 API with OAuth 1.0a
    - test_x_connection(): Test X API connectivity
"""

import os
import tempfile
import requests
import tweepy
from app.config import (
    X_CLIENT_ID, X_CLIENT_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET,
    X_API_KEY, X_API_SECRET
)
from app.auth.x_auth import get_valid_access_token, load_x_credentials


def upload_media_to_x(media_path, access_token=None, access_token_secret=None):
    """
    Upload media to X using v1.1 API with OAuth 1.0a (required for media uploads).
    
    Args:
        media_path (str): Path to media file
        access_token (str, optional): OAuth 1.0a access token
        access_token_secret (str, optional): OAuth 1.0a access token secret
        
    Returns:
        str: Media ID for attaching to tweets, or None if failed
    """
    try:
        # For media uploads, we need OAuth 1.0a credentials
        # Try to get them from various sources
        api_key = X_API_KEY or X_CLIENT_ID
        api_secret = X_API_SECRET or X_CLIENT_SECRET
        
        # Use provided tokens or try to get stored ones
        token = access_token or X_ACCESS_TOKEN
        token_secret = access_token_secret or X_ACCESS_TOKEN_SECRET
        
        # If we don't have OAuth 1.0a tokens, try to get them from stored X credentials
        if not token or not token_secret:
            credentials = load_x_credentials()
            if credentials:
                # Check if we have OAuth 1.0a tokens stored
                token = credentials.get('oauth1_access_token') or credentials.get('access_token')
                token_secret = credentials.get('oauth1_access_token_secret') or credentials.get('access_token_secret')
        
        if not all([api_key, api_secret, token, token_secret]):
            print("❌ Missing OAuth 1.0a credentials for media upload")
            print("   Media uploads require OAuth 1.0a authentication")
            print("   Please ensure X_API_KEY, X_API_SECRET and OAuth 1.0a tokens are configured")
            return None
        
        # Set up Tweepy with OAuth 1.0a for media upload
        auth = tweepy.OAuth1UserHandler(
            api_key, api_secret, token, token_secret
        )
        api = tweepy.API(auth)
        
        # Handle both file paths and file-like objects
        if hasattr(media_path, 'read'):
            # It's a file-like object, save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                media_path.seek(0)
                temp_file.write(media_path.read())
                temp_path = temp_file.name
            
            # Upload media
            media = api.simple_upload(temp_path)
            
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
        else:
            # It's a file path
            media = api.simple_upload(media_path)
        
        return str(media.media_id)
        
    except Exception as e:
        print(f"❌ Failed to upload media to X: {str(e)}")
        if "401" in str(e) or "unauthorized" in str(e).lower():
            print("   This usually means OAuth 1.0a credentials are missing or invalid")
            print("   Media uploads require separate OAuth 1.0a setup")
        return None


def create_x_post(text, media_paths=None, access_token=None):
    """
    Create a post on X (Twitter) with optional media.
    
    Args:
        text (str): Tweet text content
        media_paths (list, optional): List of media file paths
        access_token (str, optional): OAuth 2.0 access token
        
    Returns:
        dict: Response with success status and details
    """
    try:
        # Get access token
        token = access_token or get_valid_access_token()
        if not token:
            return {
                'success': False,
                'error': 'No valid X access token available',
                'platform': 'x'
            }
        
        # Prepare tweet data
        tweet_data = {'text': text}
        
        # Handle media uploads if provided
        if media_paths:
            media_ids = []
            temp_files = []
            
            try:
                for media_path in media_paths:
                    # Handle both file paths and file-like objects
                    if hasattr(media_path, 'read'):
                        # It's a file-like object, save to temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                            media_path.seek(0)
                            temp_file.write(media_path.read())
                            temp_path = temp_file.name
                            temp_files.append(temp_path)
                    else:
                        # It's a file path
                        temp_path = media_path
                    
                    # Upload media using v1.1 API
                    media_id = upload_media_to_x(temp_path)
                    if media_id:
                        media_ids.append(media_id)
                    else:
                        print(f"⚠️ Failed to upload media: {temp_path}")
                
                # Add media IDs to tweet if any were uploaded successfully
                if media_ids:
                    tweet_data['media'] = {'media_ids': media_ids}
                
            finally:
                # Clean up temporary files
                for temp_file in temp_files:
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
        
        # Post tweet using v2 API
        url = "https://api.x.com/2/tweets"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=tweet_data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        if 'data' in result and 'id' in result['data']:
            tweet_id = result['data']['id']
            tweet_url = f"https://x.com/i/web/status/{tweet_id}"
            
            return {
                'success': True,
                'post_id': tweet_id,
                'post_url': tweet_url,
                'platform': 'x',
                'message': f'Successfully posted to X: {tweet_url}'
            }
        else:
            return {
                'success': False,
                'error': f'Unexpected response format: {result}',
                'platform': 'x'
            }
            
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error: {e.response.status_code}"
        try:
            error_details = e.response.json()
            if 'errors' in error_details:
                error_msg += f" - {error_details['errors']}"
        except:
            pass
        
        return {
            'success': False,
            'error': error_msg,
            'platform': 'x'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to post to X: {str(e)}',
            'platform': 'x'
        }


def post_to_x(text, media_paths=None):
    """
    Main function to post content to X (Twitter).
    This function is called by the multi-platform posting system.
    
    Args:
        text (str): Tweet text content
        media_paths (list, optional): List of media file paths
        
    Returns:
        dict: Response with success status and details
    """
    return create_x_post(text, media_paths)


def get_user_profile():
    """
    Get the authenticated user's X profile information.
    
    Returns:
        dict: User profile data or None if failed
    """
    try:
        token = get_valid_access_token()
        if not token:
            return None
        
        url = "https://api.x.com/2/users/me"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        return result.get('data', {})
        
    except Exception as e:
        print(f"Failed to get X user profile: {e}")
        return None


def test_x_connection():
    """
    Test X API connection and credentials.
    
    Returns:
        dict: Connection test results
    """
    try:
        # Test OAuth 2.0 connection
        token = get_valid_access_token()
        if not token:
            return {
                'success': False,
                'error': 'No valid access token available',
                'details': 'Run X authentication setup'
            }
        
        # Test API call
        user_info = get_user_profile()
        if user_info and 'id' in user_info:
            return {
                'success': True,
                'user_id': user_info['id'],
                'username': user_info.get('username', 'Unknown'),
                'name': user_info.get('name', 'Unknown'),
                'message': f"Connected as @{user_info.get('username', 'unknown')}"
            }
        else:
            return {
                'success': False,
                'error': 'Failed to retrieve user information',
                'details': 'API call succeeded but returned invalid data'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Connection test failed: {str(e)}',
            'details': 'Check credentials and network connection'
        }


def get_x_posting_limits():
    """
    Get X posting limits and guidelines.
    
    Returns:
        dict: Posting limits and guidelines
    """
    return {
        'character_limit': 280,
        'media_limit': 4,  # Max 4 images or 1 video per tweet
        'supported_formats': ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov'],
        'max_video_size': '512MB',
        'max_image_size': '5MB',
        'rate_limits': {
            'tweets_per_day': 2400,  # For verified accounts
            'tweets_per_hour': 300,   # Standard limit
            'tweets_per_15min': 50    # Burst limit
        }
    }


# Load X credentials on module import
def load_x_credentials():
    """
    Load X credentials from storage.
    
    Returns:
        dict: Credentials or None if not found
    """
    from app.auth.x_auth import load_x_credentials as _load_creds
    return _load_creds()


if __name__ == "__main__":
    # Test X platform integration
    print("X Platform Integration Test")
    print("=" * 30)
    
    # Test connection
    connection_test = test_x_connection()
    if connection_test['success']:
        print(f"✅ {connection_test['message']}")
        
        # Test posting (commented out to avoid spam)
        # test_result = post_to_x("Test post from social media scheduler! 🚀")
        # if test_result['success']:
        #     print(f"✅ Test post successful: {test_result['post_url']}")
        # else:
        #     print(f"❌ Test post failed: {test_result['error']}")
        
    else:
        print(f"❌ Connection failed: {connection_test['error']}")
        print("   Run 'python scripts/x_setup.py' to set up authentication")
    
    # Show posting limits
    limits = get_x_posting_limits()
    print(f"\n📊 X Posting Limits:")
    print(f"   Character limit: {limits['character_limit']}")
    print(f"   Media limit: {limits['media_limit']} files")
    print(f"   Rate limit: {limits['rate_limits']['tweets_per_hour']}/hour") 