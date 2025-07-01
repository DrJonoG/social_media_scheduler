#!/usr/bin/env python3
"""
Pinterest OAuth2 Setup Script

This script handles Pinterest OAuth2 authentication setup for the Social Media Scheduler.
It follows the same patterns as facebook_setup.py and instagram_setup.py.

Usage:
    python scripts/pinterest_setup.py

Requirements:
    - Pinterest app credentials in .env file
    - Pinterest Developer account with approved app
    - Valid redirect URI configured in Pinterest app settings
"""

import sys
import os
import webbrowser
import time
import json
from urllib.parse import urlparse, parse_qs

# Add the project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.auth.pinterest_auth import (
    generate_pinterest_auth_url, exchange_code_for_tokens, 
    get_user_info, get_user_boards, save_pinterest_credentials
)
from app.platforms.pinterest import get_pinterest_boards_info
from app.config import PINTEREST_CLIENT_ID, PINTEREST_CLIENT_SECRET, PINTEREST_REDIRECT_URI

def print_header():
    """Print the setup script header."""
    print("=" * 60)
    print("🎨 PINTEREST OAUTH2 SETUP")
    print("=" * 60)
    print()
    print("This script will help you authenticate with Pinterest and")
    print("set up your account for posting to Pinterest boards.")
    print()

def validate_config():
    """Validate Pinterest configuration."""
    print("🔍 Validating Pinterest configuration...")
    
    missing_config = []
    
    if not PINTEREST_CLIENT_ID or PINTEREST_CLIENT_ID == "your_client_id":
        missing_config.append("PINTEREST_CLIENT_ID")
    
    if not PINTEREST_CLIENT_SECRET or PINTEREST_CLIENT_SECRET == "your_client_secret":
        missing_config.append("PINTEREST_CLIENT_SECRET")
    
    if not PINTEREST_REDIRECT_URI or PINTEREST_REDIRECT_URI == "http://localhost:8080/pinterest_callback":
        missing_config.append("PINTEREST_REDIRECT_URI (update from default)")
    
    if missing_config:
        print("❌ Missing or invalid configuration:")
        for config in missing_config:
            print(f"   - {config}")
        print()
        print("📝 Please update your .env file with valid Pinterest app credentials.")
        print("   You can get these from: https://developers.pinterest.com/")
        print()
        print("   Required in .env:")
        print("   PINTEREST_CLIENT_ID=your_actual_client_id")
        print("   PINTEREST_CLIENT_SECRET=your_actual_client_secret") 
        print("   PINTEREST_REDIRECT_URI=http://localhost:8080/pinterest_callback")
        return False
    
    print("✅ Pinterest configuration looks good!")
    print(f"   Client ID: {PINTEREST_CLIENT_ID[:8]}...")
    print(f"   Redirect URI: {PINTEREST_REDIRECT_URI}")
    print()
    return True

def get_authorization_code():
    """Handle the OAuth2 authorization flow."""
    print("🔐 Starting Pinterest OAuth2 authorization...")
    print()
    
    # Generate authorization URL
    auth_url, state = generate_pinterest_auth_url()
    
    print("📋 STEP 1: Authorization")
    print("We'll open Pinterest in your browser for authorization.")
    print()
    print("🌐 Authorization URL:")
    print(auth_url)
    print()
    
    # Open browser
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened automatically")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("Please copy and paste the URL above into your browser")
    
    print()
    print("📋 STEP 2: Get Authorization Code")
    print("After authorizing the app, Pinterest will redirect you to:")
    print(f"   {PINTEREST_REDIRECT_URI}")
    print()
    print("The URL will contain a 'code' parameter, like:")
    print("   http://localhost:8080/pinterest_callback?code=ABC123&state=xyz")
    print()
    
    # Get the authorization code from user
    while True:
        callback_url = input("📥 Paste the full callback URL here: ").strip()
        
        if not callback_url:
            print("❌ Please provide the callback URL")
            continue
        
        # Parse the callback URL
        try:
            parsed_url = urlparse(callback_url)
            query_params = parse_qs(parsed_url.query)
            
            if 'code' not in query_params:
                print("❌ No authorization code found in URL")
                print("   Make sure you copied the complete URL after authorization")
                continue
            
            auth_code = query_params['code'][0]
            
            # Verify state parameter if present
            if 'state' in query_params:
                received_state = query_params['state'][0]
                if received_state != state:
                    print("⚠️  State parameter mismatch - this might be a security issue")
                    choice = input("Continue anyway? (y/N): ").strip().lower()
                    if choice != 'y':
                        continue
            
            return auth_code
            
        except Exception as e:
            print(f"❌ Error parsing callback URL: {e}")
            print("   Please make sure you copied the complete URL")
            continue

def exchange_tokens(auth_code):
    """Exchange authorization code for access tokens."""
    print()
    print("🔄 Exchanging authorization code for access tokens...")
    
    try:
        token_data = exchange_code_for_tokens(auth_code)
        
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        
        if not access_token:
            raise Exception("No access token received")
        
        print("✅ Successfully obtained access tokens!")
        print(f"   Access Token: {access_token[:20]}...")
        if refresh_token:
            print(f"   Refresh Token: {refresh_token[:20]}...")
        else:
            print("   Note: No refresh token provided")
        
        return token_data
        
    except Exception as e:
        print(f"❌ Failed to exchange tokens: {e}")
        return None

def get_account_info(access_token):
    """Get Pinterest account information."""
    print()
    print("👤 Fetching Pinterest account information...")
    
    try:
        # Get user info
        user_info = get_user_info(access_token)
        
        user_id = user_info.get("id", "")
        username = user_info.get("username", "")
        profile_image = user_info.get("profile_image", "")
        account_type = user_info.get("account_type", "")
        
        print("✅ Account information retrieved:")
        print(f"   User ID: {user_id}")
        print(f"   Username: @{username}")
        print(f"   Account Type: {account_type}")
        
        # Get user's boards
        print()
        print("📌 Fetching Pinterest boards...")
        
        try:
            boards_data = get_user_boards(access_token)
            boards = boards_data.get("items", [])
            
            print(f"✅ Found {len(boards)} board(s):")
            for i, board in enumerate(boards[:5], 1):  # Show first 5 boards
                board_name = board.get("name", "Untitled")
                pin_count = board.get("pin_count", 0)
                privacy = board.get("privacy", "unknown")
                print(f"   {i}. {board_name} ({pin_count} pins, {privacy})")
            
            if len(boards) > 5:
                print(f"   ... and {len(boards) - 5} more boards")
            
            # Format boards for storage
            boards_info = []
            for board in boards:
                boards_info.append({
                    "id": board.get("id", ""),
                    "name": board.get("name", ""),
                    "description": board.get("description", ""),
                    "pin_count": board.get("pin_count", 0),
                    "privacy": board.get("privacy", "public")
                })
            
        except Exception as e:
            print(f"⚠️  Could not fetch boards: {e}")
            boards_info = []
        
        return {
            "user_id": user_id,
            "username": username,
            "profile_image": profile_image,
            "account_type": account_type,
            "boards": boards_info
        }
        
    except Exception as e:
        print(f"❌ Failed to get account information: {e}")
        return None

def save_credentials(token_data, account_info):
    """Save Pinterest credentials to storage."""
    print()
    print("💾 Saving Pinterest credentials...")
    
    try:
        # Combine token data and account info
        credentials = {
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "token_type": token_data.get("token_type", "Bearer"),
            "scope": token_data.get("scope", ""),
            **account_info
        }
        
        # Save credentials
        success = save_pinterest_credentials(credentials)
        
        if success:
            print("✅ Pinterest credentials saved successfully!")
            
            from app.config import USE_DATABASE
            if USE_DATABASE:
                print("   📊 Stored in database")
            else:
                print("   📁 Stored in app/secure/pinterest_token.json")
        else:
            print("❌ Failed to save Pinterest credentials")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving credentials: {e}")
        return False

def test_connection():
    """Test the Pinterest connection."""
    print()
    print("🧪 Testing Pinterest connection...")
    
    try:
        from app.platforms.pinterest import test_pinterest_connection
        
        if test_pinterest_connection():
            print("✅ Pinterest connection test successful!")
            return True
        else:
            print("❌ Pinterest connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print()
    print("=" * 60)
    print("🎉 PINTEREST SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("✅ Your Pinterest account is now connected and ready to use!")
    print()
    print("📋 Next Steps:")
    print("1. Run the main application:")
    print("   python main.py")
    print()
    print("2. In the dashboard:")
    print("   - Select 'Pinterest' as one of your platforms")
    print("   - Create your content with media (images work best)")
    print("   - Post to your Pinterest boards!")
    print()
    print("💡 Tips:")
    print("   - Pinterest works best with vertical images (2:3 ratio)")
    print("   - Use engaging titles and descriptions")
    print("   - Include relevant keywords for discoverability")
    print("   - Pins will be posted to your default board")
    print()
    print("🔧 Troubleshooting:")
    print("   - If posting fails, re-run this setup script")
    print("   - Check that your Pinterest app has the correct permissions")
    print("   - Ensure your boards are public or accessible")
    print()

def main():
    """Main setup function."""
    try:
        print_header()
        
        # Validate configuration
        if not validate_config():
            return
        
        # Get authorization code
        auth_code = get_authorization_code()
        if not auth_code:
            print("❌ Setup cancelled - no authorization code provided")
            return
        
        # Exchange for tokens
        token_data = exchange_tokens(auth_code)
        if not token_data:
            return
        
        # Get account information
        account_info = get_account_info(token_data["access_token"])
        if not account_info:
            return
        
        # Save credentials
        if not save_credentials(token_data, account_info):
            return
        
        # Test connection
        test_connection()
        
        # Print next steps
        print_next_steps()
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        print("\nPlease check your configuration and try again.")

if __name__ == "__main__":
    main()
