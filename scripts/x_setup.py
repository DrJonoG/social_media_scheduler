#!/usr/bin/env python3
"""
X (Twitter) Authentication Setup Script

This script guides you through setting up OAuth 2.0 authentication for X (Twitter) API.
X uses OAuth 2.0 Authorization Code Flow with PKCE for enhanced security.

Prerequisites:
1. X Developer Account with approved app
2. X app configured with OAuth 2.0 enabled
3. Redirect URI configured in X app settings
4. Environment variables set in .env file

Run this script to:
- Generate OAuth 2.0 authorization URL
- Handle the authorization callback
- Exchange authorization code for tokens
- Test the connection
- Save credentials securely
"""

import os
import sys
import json
import webbrowser
from urllib.parse import urlparse, parse_qs

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import X_CLIENT_ID, X_CLIENT_SECRET, X_REDIRECT_URI
from app.auth.x_auth import (
    generate_x_auth_url, exchange_code_for_tokens, get_user_info,
    save_x_credentials, validate_access_token
)
from app.platforms.x import test_x_connection


def print_header():
    """Print script header and information."""
    print("=" * 60)
    print("🐦 X (Twitter) Authentication Setup")
    print("=" * 60)
    print()
    print("This script will help you set up OAuth 2.0 authentication for X.")
    print("Make sure you have:")
    print("✓ X Developer Account with approved app")
    print("✓ OAuth 2.0 enabled in your X app settings")
    print("✓ Redirect URI configured in X app")
    print("✓ Environment variables set in .env file")
    print()


def check_configuration():
    """Check if required configuration is present."""
    print("🔍 Checking configuration...")
    
    missing_config = []
    
    if not X_CLIENT_ID:
        missing_config.append("X_CLIENT_ID")
    
    if not X_CLIENT_SECRET:
        missing_config.append("X_CLIENT_SECRET")
    
    if not X_REDIRECT_URI:
        missing_config.append("X_REDIRECT_URI")
    
    if missing_config:
        print("❌ Missing required configuration:")
        for config in missing_config:
            print(f"   - {config}")
        print()
        print("Please add these to your .env file:")
        print("X_CLIENT_ID=your_client_id")
        print("X_CLIENT_SECRET=your_client_secret")
        print("X_REDIRECT_URI=http://localhost:8080/callback")
        print()
        print("Get these from: https://developer.x.com/")
        return False
    
    print("✅ Configuration looks good!")
    print(f"   Client ID: {X_CLIENT_ID[:10]}...")
    print(f"   Redirect URI: {X_REDIRECT_URI}")
    print()
    return True


def get_authorization_code():
    """Handle the OAuth 2.0 authorization flow."""
    print("🔐 Starting OAuth 2.0 authorization flow...")
    
    try:
        # Generate authorization URL with PKCE
        auth_url, state, code_verifier = generate_x_auth_url()
        
        print("📋 Authorization URL generated with PKCE security")
        print(f"   State: {state[:20]}...")
        print(f"   Code verifier: {code_verifier[:20]}...")
        print()
        
        # Open browser for authorization
        print("🌐 Opening browser for authorization...")
        print("   If browser doesn't open, copy this URL:")
        print(f"   {auth_url}")
        print()
        
        webbrowser.open(auth_url)
        
        # Get callback URL from user
        print("📥 After authorizing, you'll be redirected to your callback URL.")
        print("   Copy the FULL URL from your browser and paste it here.")
        print()
        
        callback_url = input("Paste the callback URL here: ").strip()
        
        if not callback_url:
            raise ValueError("No callback URL provided")
        
        # Parse callback URL
        parsed_url = urlparse(callback_url)
        query_params = parse_qs(parsed_url.query)
        
        # Extract authorization code and state
        if 'code' not in query_params:
            if 'error' in query_params:
                error = query_params['error'][0]
                error_description = query_params.get('error_description', ['Unknown error'])[0]
                raise ValueError(f"Authorization failed: {error} - {error_description}")
            else:
                raise ValueError("No authorization code found in callback URL")
        
        authorization_code = query_params['code'][0]
        returned_state = query_params.get('state', [None])[0]
        
        # Validate state parameter
        if returned_state != state:
            raise ValueError("State parameter mismatch - possible CSRF attack")
        
        print("✅ Authorization code received successfully!")
        print(f"   Code: {authorization_code[:20]}...")
        print()
        
        return authorization_code, code_verifier
        
    except Exception as e:
        print(f"❌ Authorization failed: {str(e)}")
        return None, None


def exchange_tokens(authorization_code, code_verifier):
    """Exchange authorization code for access tokens."""
    print("🔄 Exchanging authorization code for tokens...")
    
    try:
        # Exchange code for tokens
        token_response = exchange_code_for_tokens(authorization_code, code_verifier)
        
        print("✅ Token exchange successful!")
        print(f"   Access token: {token_response['access_token'][:20]}...")
        
        if 'refresh_token' in token_response:
            print(f"   Refresh token: {token_response['refresh_token'][:20]}...")
        else:
            print("   ⚠️ No refresh token received (offline.access scope might be missing)")
        
        if 'expires_in' in token_response:
            expires_in_hours = token_response['expires_in'] / 3600
            print(f"   Expires in: {expires_in_hours:.1f} hours")
        
        print()
        return token_response
        
    except Exception as e:
        print(f"❌ Token exchange failed: {str(e)}")
        return None


def get_account_info(access_token):
    """Get and display account information."""
    print("👤 Getting account information...")
    
    try:
        user_info = get_user_info(access_token)
        
        print("✅ Account information retrieved!")
        print(f"   User ID: {user_info['id']}")
        print(f"   Username: @{user_info['username']}")
        print(f"   Display Name: {user_info['name']}")
        
        if 'description' in user_info:
            description = user_info['description']
            if len(description) > 50:
                description = description[:50] + "..."
            print(f"   Bio: {description}")
        
        if 'public_metrics' in user_info:
            metrics = user_info['public_metrics']
            print(f"   Followers: {metrics.get('followers_count', 'N/A')}")
            print(f"   Following: {metrics.get('following_count', 'N/A')}")
            print(f"   Tweets: {metrics.get('tweet_count', 'N/A')}")
        
        print()
        return user_info
        
    except Exception as e:
        print(f"❌ Failed to get account info: {str(e)}")
        return None


def save_credentials(token_response, user_info):
    """Save credentials to storage."""
    print("💾 Saving credentials...")
    
    try:
        # Prepare credentials data
        credentials = {
            'access_token': token_response['access_token'],
            'token_type': token_response.get('token_type', 'bearer'),
            'expires_in': token_response.get('expires_in'),
            'scope': token_response.get('scope'),
            'user_id': user_info['id'],
            'username': user_info['username'],
            'name': user_info['name']
        }
        
        # Include refresh token if available
        if 'refresh_token' in token_response:
            credentials['refresh_token'] = token_response['refresh_token']
        
        # Save credentials
        save_x_credentials(credentials)
        
        print("✅ Credentials saved successfully!")
        print("   Stored in database/file based on configuration")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save credentials: {str(e)}")
        return False


def test_connection():
    """Test the X API connection."""
    print("🧪 Testing X API connection...")
    
    try:
        connection_test = test_x_connection()
        
        if connection_test['success']:
            print("✅ Connection test successful!")
            print(f"   Connected as: @{connection_test['username']}")
            print(f"   User ID: {connection_test['user_id']}")
            print(f"   Display Name: {connection_test['name']}")
        else:
            print("❌ Connection test failed!")
            print(f"   Error: {connection_test['error']}")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Connection test error: {str(e)}")
        return False


def show_next_steps():
    """Show next steps after successful setup."""
    print("🎉 X authentication setup complete!")
    print()
    print("Next steps:")
    print("1. ✅ X is now configured and ready to use")
    print("2. 🚀 Run the main application: python main.py")
    print("3. 📝 Select X in the platform selection")
    print("4. 🎯 Create and schedule your posts")
    print()
    print("📋 X API Features Available:")
    print("   • Text posts (280 character limit)")
    print("   • Image posts (up to 4 images)")
    print("   • Video posts (single video)")
    print("   • Scheduled posting")
    print("   • Multi-platform posting")
    print()
    print("⚠️ Important Notes:")
    print("   • Access tokens expire in 2 hours by default")
    print("   • Refresh tokens allow automatic renewal")
    print("   • Rate limits: 300 tweets/hour for standard accounts")
    print("   • Media uploads require OAuth 1.0a credentials")
    print()


def main():
    """Main setup function."""
    print_header()
    
    # Check configuration
    if not check_configuration():
        return
    
    # Get authorization
    authorization_code, code_verifier = get_authorization_code()
    if not authorization_code:
        return
    
    # Exchange for tokens
    token_response = exchange_tokens(authorization_code, code_verifier)
    if not token_response:
        return
    
    # Get account info
    user_info = get_account_info(token_response['access_token'])
    if not user_info:
        return
    
    # Save credentials
    if not save_credentials(token_response, user_info):
        return
    
    # Test connection
    if not test_connection():
        return
    
    # Show next steps
    show_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        print("Please check your configuration and try again.")
        sys.exit(1) 