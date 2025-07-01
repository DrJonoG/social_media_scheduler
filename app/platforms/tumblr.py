"""
Tumblr Platform API Module

This module provides functions for interacting with the Tumblr API,
including posting content, retrieving user information, and managing blog operations.
Uses OAuth 1.0a authentication.
"""

import os
import json
import logging
import tempfile
import requests
from requests_oauthlib import OAuth1Session
from urllib.parse import urlparse
from app.auth.tumblr_auth import load_tumblr_credentials

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tumblr API configuration
TUMBLR_API_BASE_URL = "https://api.tumblr.com/v2"

def create_oauth_session(access_token, access_token_secret):
    """
    Create an authenticated OAuth session for Tumblr API calls.
    
    Args:
        access_token (str): OAuth access token
        access_token_secret (str): OAuth access token secret
        
    Returns:
        OAuth1Session: Authenticated session object
    """
    client_key = os.getenv('TUMBLR_CLIENT_ID')
    client_secret = os.getenv('TUMBLR_CLIENT_SECRET')
    
    return OAuth1Session(
        client_key,
        client_secret=client_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret
    )

def upload_media_to_tumblr(media_path, access_token, access_token_secret):
    """
    Upload media file to Tumblr (handled during post creation).
    
    Args:
        media_path (str): Path to the media file
        access_token (str): OAuth access token
        access_token_secret (str): OAuth access token secret
        
    Returns:
        str: Media path (Tumblr handles upload during post creation)
    """
    try:
        # Tumblr handles media upload during post creation
        # We just need to ensure the file exists and is accessible
        if os.path.exists(media_path):
            logger.info(f"Media file ready for Tumblr upload: {media_path}")
            return media_path
        else:
            logger.error(f"Media file not found: {media_path}")
            return None
    except Exception as e:
        logger.error(f"Error preparing media for Tumblr: {e}")
        return None

def get_user_blogs(access_token, access_token_secret):
    """
    Get list of user's blogs from Tumblr.
    
    Args:
        access_token (str): OAuth access token
        access_token_secret (str): OAuth access token secret
        
    Returns:
        list: List of user's blogs
    """
    try:
        oauth = create_oauth_session(access_token, access_token_secret)
        
        response = oauth.get(f"{TUMBLR_API_BASE_URL}/user/info")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('meta', {}).get('status') == 200:
                user_data = data.get('response', {}).get('user', {})
                blogs = user_data.get('blogs', [])
                
                return [{
                    'id': blog.get('name', ''),
                    'name': blog.get('name', ''),
                    'title': blog.get('title', ''),
                    'url': blog.get('url', ''),
                    'primary': blog.get('primary', False),
                    'followers': blog.get('followers', 0),
                    'posts': blog.get('posts', 0)
                } for blog in blogs]
        
        logger.error(f"Failed to get user blogs: {response.status_code}")
        return []
        
    except Exception as e:
        logger.error(f"Error getting user blogs: {e}")
        return []

def create_tumblr_post(blog_name, post_data, access_token, access_token_secret):
    """
    Create a post on Tumblr using the legacy API.
    
    Args:
        blog_name (str): The blog identifier (name)
        post_data (dict): Post data including type, content, etc.
        access_token (str): OAuth access token
        access_token_secret (str): OAuth access token secret
        
    Returns:
        dict: Response from Tumblr API
    """
    try:
        oauth = create_oauth_session(access_token, access_token_secret)
        
        url = f"{TUMBLR_API_BASE_URL}/blog/{blog_name}/post"
        
        # Handle media upload if present
        files = None
        if 'media_path' in post_data and post_data['media_path']:
            try:
                with open(post_data['media_path'], 'rb') as f:
                    files = {'data': f}
                    # Remove media_path from post_data as it's now in files
                    post_data_copy = post_data.copy()
                    del post_data_copy['media_path']
                    
                    response = oauth.post(url, data=post_data_copy, files=files)
            except Exception as e:
                logger.error(f"Error uploading media: {e}")
                # Fall back to posting without media
                response = oauth.post(url, data=post_data)
        else:
            response = oauth.post(url, data=post_data)
        
        if response.status_code == 201:
            data = response.json()
            if data.get('meta', {}).get('status') == 201:
                post_id = data.get('response', {}).get('id')
                return {
                    'success': True,
                    'post_id': str(post_id),
                    'message': 'Post created successfully on Tumblr'
                }
        
        logger.error(f"Failed to create Tumblr post: {response.status_code} - {response.text}")
        return {
            'success': False,
            'error': f"HTTP {response.status_code}: {response.text[:200]}"
        }
        
    except Exception as e:
        logger.error(f"Error creating Tumblr post: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def post_to_tumblr(message, media_path=None, user_id=None):
    """
    Post content to Tumblr.
    
    Args:
        message (str): The message/content to post
        media_path (str, optional): Path to media file to upload
        user_id (str, optional): User identifier for credential lookup
        
    Returns:
        dict: Result of the posting operation
    """
    try:
        # Load credentials
        credentials = load_tumblr_credentials(user_id)
        if not credentials:
            return {
                'success': False,
                'error': 'No Tumblr credentials found. Please authenticate first.'
            }
        
        access_token = credentials.get('access_token')
        access_token_secret = credentials.get('access_token_secret')
        
        if not access_token or not access_token_secret:
            return {
                'success': False,
                'error': 'Invalid Tumblr credentials found.'
            }
        
        # Get user's blogs to find primary blog
        blogs = get_user_blogs(access_token, access_token_secret)
        if not blogs:
            return {
                'success': False,
                'error': 'Could not retrieve user blogs.'
            }
        
        # Use primary blog or first available blog
        primary_blog = next((blog for blog in blogs if blog.get('primary')), blogs[0])
        blog_name = primary_blog.get('name')
        
        if not blog_name:
            return {
                'success': False,
                'error': 'Could not determine blog name for posting.'
            }
        
        # Prepare post data
        if media_path and os.path.exists(media_path):
            # Determine media type
            file_extension = os.path.splitext(media_path)[1].lower()
            
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
                # Photo post
                post_data = {
                    'type': 'photo',
                    'caption': message,
                    'media_path': media_path
                }
            elif file_extension in ['.mp4', '.mov', '.avi']:
                # Video post
                post_data = {
                    'type': 'video',
                    'caption': message,
                    'media_path': media_path
                }
            else:
                # Fallback to text post with link
                post_data = {
                    'type': 'text',
                    'title': 'Social Media Post',
                    'body': message
                }
        else:
            # Text post
            # Split message into title and body for better formatting
            lines = message.split('\n', 1)
            title = lines[0][:100] if lines[0] else "Social Media Post"  # Tumblr title limit
            body = message
            
            post_data = {
                'type': 'text',
                'title': title,
                'body': body,
                'format': 'html'
            }
        
        # Add common post parameters
        post_data.update({
            'state': 'published',
            'tags': 'social-media-scheduler'
        })
        
        # Create the post
        result = create_tumblr_post(blog_name, post_data, access_token, access_token_secret)
        
        if result.get('success'):
            logger.info(f"Successfully posted to Tumblr blog: {blog_name}")
            return {
                'success': True,
                'platform': 'Tumblr',
                'post_id': result.get('post_id'),
                'message': f"Posted to Tumblr blog: {primary_blog.get('title', blog_name)}",
                'blog_name': blog_name,
                'blog_title': primary_blog.get('title', blog_name)
            }
        else:
            return {
                'success': False,
                'platform': 'Tumblr',
                'error': result.get('error', 'Unknown error occurred')
            }
        
    except Exception as e:
        logger.error(f"Error posting to Tumblr: {e}")
        return {
            'success': False,
            'platform': 'Tumblr',
            'error': str(e)
        }

def get_tumblr_user_info(user_id=None):
    """
    Get Tumblr user information.
    
    Args:
        user_id (str, optional): User identifier for credential lookup
        
    Returns:
        dict: User information or None if error
    """
    try:
        credentials = load_tumblr_credentials(user_id)
        if not credentials:
            return None
        
        access_token = credentials.get('access_token')
        access_token_secret = credentials.get('access_token_secret')
        
        if not access_token or not access_token_secret:
            return None
        
        oauth = create_oauth_session(access_token, access_token_secret)
        
        response = oauth.get(f"{TUMBLR_API_BASE_URL}/user/info")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('meta', {}).get('status') == 200:
                user_data = data.get('response', {}).get('user', {})
                blogs = user_data.get('blogs', [])
                primary_blog = next((blog for blog in blogs if blog.get('primary')), blogs[0] if blogs else {})
                
                return {
                    'username': user_data.get('name', 'Unknown'),
                    'blog_name': primary_blog.get('name', ''),
                    'blog_title': primary_blog.get('title', ''),
                    'blog_url': primary_blog.get('url', ''),
                    'followers': primary_blog.get('followers', 0),
                    'following': user_data.get('following', 0),
                    'total_blogs': len(blogs),
                    'posts': primary_blog.get('posts', 0)
                }
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting Tumblr user info: {e}")
        return None

def validate_tumblr_credentials(user_id=None):
    """
    Validate Tumblr credentials by making a test API call.
    
    Args:
        user_id (str, optional): User identifier for credential lookup
        
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    try:
        user_info = get_tumblr_user_info(user_id)
        return user_info is not None
    except Exception as e:
        logger.error(f"Error validating Tumblr credentials: {e}")
        return False

def get_tumblr_blogs_info(user_id=None):
    """
    Get information about user's Tumblr blogs.
    
    Args:
        user_id (str, optional): User identifier for credential lookup
        
    Returns:
        list: List of blog information
    """
    try:
        credentials = load_tumblr_credentials(user_id)
        if not credentials:
            return []
        
        access_token = credentials.get('access_token')
        access_token_secret = credentials.get('access_token_secret')
        
        if not access_token or not access_token_secret:
            return []
        
        return get_user_blogs(access_token, access_token_secret)
        
    except Exception as e:
        logger.error(f"Error getting Tumblr blogs info: {e}")
        return []

def test_tumblr_connection(user_id=None):
    """
    Test the Tumblr API connection.
    
    Args:
        user_id (str, optional): User identifier for credential lookup
        
    Returns:
        dict: Connection test results
    """
    try:
        user_info = get_tumblr_user_info(user_id)
        
        if user_info:
            blogs = get_tumblr_blogs_info(user_id)
            
            return {
                'success': True,
                'platform': 'Tumblr',
                'user_info': user_info,
                'blogs': blogs,
                'message': f"Connected to Tumblr as {user_info.get('username')} with {len(blogs)} blog(s)"
            }
        else:
            return {
                'success': False,
                'platform': 'Tumblr',
                'error': 'Failed to retrieve user information. Please check your credentials.'
            }
        
    except Exception as e:
        logger.error(f"Error testing Tumblr connection: {e}")
        return {
            'success': False,
            'platform': 'Tumblr',
            'error': str(e)
        }

# Utility functions for post formatting

def format_tumblr_text_post(message, title=None):
    """
    Format content for a Tumblr text post.
    
    Args:
        message (str): The main message content
        title (str, optional): Post title
        
    Returns:
        dict: Formatted post data
    """
    if not title:
        # Extract title from first line if not provided
        lines = message.split('\n', 1)
        title = lines[0][:100] if lines[0] else "Social Media Post"
    
    return {
        'type': 'text',
        'title': title,
        'body': message,
        'format': 'html'
    }

def format_tumblr_photo_post(message, media_path):
    """
    Format content for a Tumblr photo post.
    
    Args:
        message (str): Caption for the photo
        media_path (str): Path to the image file
        
    Returns:
        dict: Formatted post data
    """
    return {
        'type': 'photo',
        'caption': message,
        'media_path': media_path
    }

def format_tumblr_link_post(url, title=None, description=None):
    """
    Format content for a Tumblr link post.
    
    Args:
        url (str): The URL to share
        title (str, optional): Title for the link
        description (str, optional): Description of the link
        
    Returns:
        dict: Formatted post data
    """
    if not title:
        # Try to extract domain as title
        try:
            parsed_url = urlparse(url)
            title = parsed_url.netloc or "Shared Link"
        except:
            title = "Shared Link"
    
    return {
        'type': 'link',
        'url': url,
        'title': title,
        'description': description or ''
    } 