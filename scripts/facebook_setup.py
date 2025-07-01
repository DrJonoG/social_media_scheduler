#!/usr/bin/env python3
"""
Facebook Authentication Setup

This script handles Facebook OAuth2 authentication and retrieves page access tokens.
Supports both database and file-based storage depending on USE_DATABASE setting.

Usage:
    python scripts/facebook_setup.py
"""

import json
import os
import sys
from pathlib import Path

# Add the parent directory to the path to import app modules
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.auth.facebook_auth import get_facebook_login_url, fetch_facebook_token
from app.platforms.facebook import get_user_pages
from app.config import USE_DATABASE, FACEBOOK_ACCESS_TOKEN

# Only import database functions if database is being used
if USE_DATABASE:
    from app.db.database import execute_query


def upsert_platform_account(platform, page_id, access_token, display_name):
    """
    Insert or update platform account in database.
    
    Args:
        platform (str): Platform name (e.g., 'facebook')
        page_id (str): Platform-specific page/account ID
        access_token (str): Access token for the account
        display_name (str): Human-readable name for the account
    """
    query_check = "SELECT id FROM platform_accounts WHERE page_id = %s AND platform = %s"
    existing = execute_query(query_check, (page_id, platform), fetch=True)

    if existing:
        query_update = """
            UPDATE platform_accounts
            SET access_token = %s, display_name = %s
            WHERE id = %s
        """
        execute_query(query_update, (access_token, display_name, existing[0]['id']))
        print(f"✅ Updated token for page: {display_name}")
    else:
        query_insert = """
            INSERT INTO platform_accounts (platform, page_id, access_token, display_name)
            VALUES (%s, %s, %s, %s)
        """
        execute_query(query_insert, (platform, page_id, access_token, display_name))
        print(f"✅ Inserted new platform account: {display_name}")


def save_facebook_tokens(token_data: dict) -> bool:
    """
    Saves Facebook page tokens to the secure directory.
    
    Args:
        token_data (dict): Token data from Facebook API
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        # Ensure secure directory exists
        secure_dir = Path(__file__).parent.parent / "app" / "secure"
        secure_dir.mkdir(exist_ok=True)
        
        # Save token data
        token_file = secure_dir / "facebook_token.json"
        with open(token_file, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print(f"✅ Facebook tokens saved to: {token_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving tokens: {e}")
        return False


def process_pages(pages_data: dict) -> bool:
    """
    Process and save Facebook page data based on USE_DATABASE configuration.
    
    Args:
        pages_data (dict): Page data from Facebook API
        
    Returns:
        bool: True if processing successful, False otherwise
    """
    try:
        if USE_DATABASE:
            print("💾 Saving to database...")
            for page in pages_data.get("data", []):
                upsert_platform_account(
                    platform="facebook",
                    page_id=page["id"],
                    access_token=page["access_token"],
                    display_name=page["name"]
                )
            print("✅ Successfully saved to database!")
        else:
            print("💾 Saving to file...")
            success = save_facebook_tokens(pages_data)
            if success:
                print("✅ Successfully saved to file!")
            else:
                return False
        
        return True
        
    except Exception as e:
        storage_type = "database" if USE_DATABASE else "file"
        print(f"❌ Error saving to {storage_type}: {e}")
        
        if USE_DATABASE:
            print("💡 Hint: Make sure your database tables are created")
            print("   You can find the SQL script in app/db/mysql_create_tables.sql")
        
        return False


def main():
    """Main function to handle Facebook authentication and token fetching."""
    
    print("🔗 Facebook Page Token Fetcher")
    print("=" * 40)
    print(f"📊 Storage mode: {'Database' if USE_DATABASE else 'File-based'}")
    
    # Check if we already have a token in environment
    if FACEBOOK_ACCESS_TOKEN:
        print("🔑 Using existing access token from environment...")
        try:
            pages_data = get_user_pages(FACEBOOK_ACCESS_TOKEN)
            
            if not pages_data.get('data'):
                print("❌ No Facebook pages found with existing token.")
                print("💡 The token may be expired. Let's get a new one...")
            else:
                print(f"📊 Found {len(pages_data['data'])} page(s):")
                for i, page in enumerate(pages_data['data']):
                    print(f"   {i+1}. {page['name']} (ID: {page['id']})")
                
                if process_pages(pages_data):
                    print("\n🎉 Token processing complete!")
                    return
                    
        except Exception as e:
            print(f"❌ Error with existing token: {e}")
            print("💡 Let's get a fresh token...")
    
    # Interactive token fetching
    try:
        # Step 1: Get and display the login URL
        print("\n📱 Step 1: Getting authentication URL...")
        auth_url = get_facebook_login_url()
        print("\n🌐 Please go to this URL and log in:")
        print(f"   {auth_url}")
        print("\n📋 After logging in, you'll be redirected to a URL starting with your redirect URI.")
        print("   Copy that ENTIRE URL and paste it below.\n")
        
        # Step 2: Get the redirect response from user
        redirect_response = input("📥 Paste the full redirect URL here: ").strip()
        
        if not redirect_response:
            print("❌ No URL provided. Exiting.")
            return
        
        # Step 3: Fetch the access token
        print("\n🔑 Step 2: Fetching access token...")
        token_data = fetch_facebook_token(redirect_response)
        user_token = token_data.get('access_token')
        
        if not user_token:
            print("❌ Failed to get access token")
            return
            
        print("✅ User access token obtained")
        
        # Step 4: Get user's pages
        print("\n📄 Step 3: Fetching your Facebook pages...")
        pages_data = get_user_pages(user_token)
        
        if not pages_data.get('data'):
            print("❌ No Facebook pages found. Make sure your account manages at least one page.")
            return
        
        # Step 5: Display pages
        print(f"\n📊 Found {len(pages_data['data'])} page(s):")
        for i, page in enumerate(pages_data['data']):
            print(f"   {i+1}. {page['name']} (ID: {page['id']})")
        
        # Step 6: Process and save the tokens
        print(f"\n💾 Step 4: Saving page tokens ({'to database' if USE_DATABASE else 'to file'})...")
        if process_pages(pages_data):
            print("\n🎉 Setup complete! You can now use Facebook posting in the dashboard.")
            print("\n💡 Next steps:")
            print("   1. Run the dashboard: streamlit run app/ui/dashboard.py")
            print("   2. Select Facebook as your platform")
            print("   3. Toggle 'Post Now' and start posting!")
        else:
            print("\n❌ Failed to save tokens. Please check permissions and try again.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        print("💡 Please check your .env file has the correct Facebook app credentials")


if __name__ == "__main__":
    main()
