#!/usr/bin/env python3
"""
Instagram Authentication Setup

This script handles Instagram OAuth2 authentication and retrieves Business Account credentials.
Stores them securely (either in database or JSON file).

Usage:
    python scripts/instagram_setup.py
"""

import json
import os
import sys
from pathlib import Path

# Add the parent directory to the path to import app modules
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.auth.instagram_auth import get_instagram_login_url, fetch_instagram_token
from app.platforms.instagram import get_instagram_business_account
from app.config import USE_DATABASE, INSTAGRAM_ACCESS_TOKEN

if USE_DATABASE:
    from app.db.database import execute_query

def upsert_platform_account(platform, page_id, access_token, display_name):
    """
    Insert or update platform account in database.
    
    Args:
        platform (str): Platform name (e.g., 'instagram')
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
        print(f"✅ Updated token for account: {display_name}")
    else:
        query_insert = """
            INSERT INTO platform_accounts (platform, page_id, access_token, display_name)
            VALUES (%s, %s, %s, %s)
        """
        execute_query(query_insert, (platform, page_id, access_token, display_name))
        print(f"✅ Inserted new platform account: {display_name}")

def save_instagram_token(data: dict) -> bool:
    """
    Save Instagram token data to JSON file.
    
    Args:
        data (dict): Token data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        secure_dir = Path(__file__).parent.parent / "app" / "secure"
        secure_dir.mkdir(exist_ok=True)

        token_file = secure_dir / "instagram_token.json"
        with open(token_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✅ Instagram tokens saved to: {token_file}")
        return True

    except Exception as e:
        print(f"❌ Error saving Instagram tokens: {e}")
        return False

def main():
    """Main function to handle Instagram authentication and token fetching."""
    
    print("🔗 Instagram Token Setup")
    print("=" * 40)
    print(f"📊 Storage mode: {'Database' if USE_DATABASE else 'File-based'}")

    # Check if we already have a token in environment
    if INSTAGRAM_ACCESS_TOKEN:
        print("🔑 Using existing access token from environment...")
        access_token = INSTAGRAM_ACCESS_TOKEN
        try:
            business_account_info = get_instagram_business_account(access_token)
            ig_user_id = business_account_info.get('id')
            ig_username = business_account_info.get('username', 'Instagram Account')

            if not ig_user_id:
                print("❌ Failed to retrieve Instagram Business Account ID with existing token.")
                print("💡 The token may be expired. Let's get a new one...")
            else:
                print(f"📊 Found Instagram Business Account: {ig_username} (ID: {ig_user_id})")
                
                # Save the credentials
                if USE_DATABASE:
                    upsert_platform_account(
                        platform="instagram",
                        page_id=ig_user_id,
                        access_token=access_token,
                        display_name=ig_username
                    )
                else:
                    save_instagram_token({
                        "access_token": access_token,
                        "ig_user_id": ig_user_id,
                        "username": ig_username
                    })
                
                print("\n🎉 Setup complete!")
                return
                
        except Exception as e:
            print(f"❌ Error with existing token: {e}")
            print("💡 Let's get a fresh token...")

    # Interactive token fetching
    try:
        # Step 1: Get and display the login URL
        print("\n📱 Step 1: Getting authentication URL...")
        auth_url = get_instagram_login_url()
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
        token_data = fetch_instagram_token(redirect_response)
        
        # Instagram uses Facebook's OAuth2, so the response format is the same
        access_token = token_data.get('access_token')
        user_id = token_data.get('user_id')
        
        if not access_token:
            print("❌ Failed to get access token")
            print(f"Response: {token_data}")
            return
            
        print("✅ User access token obtained")
        
        # Step 4: Get Instagram Business Account info
        print("\n📄 Step 3: Fetching Instagram Business Account information...")
        business_account_info = get_instagram_business_account(access_token)
        
        if 'error' in business_account_info:
            print(f"❌ {business_account_info['error']}")
            print("💡 Make sure you have:")
            print("   1. A Facebook page with admin access")
            print("   2. An Instagram Business/Creator account")
            print("   3. The Instagram account linked to your Facebook page")
            print("   4. Go to your Facebook page settings > Instagram > Connect Account")
            return
        
        ig_user_id = business_account_info.get('id')
        ig_username = business_account_info.get('username', 'Instagram Account')
        page_token = business_account_info.get('page_access_token')
        
        if not ig_user_id:
            print("❌ Failed to retrieve Instagram Business Account ID.")
            return
        
        # Step 5: Display account info
        print(f"\n📊 Found Instagram Business Account:")
        print(f"   Username: {ig_username}")
        print(f"   ID: {ig_user_id}")
        
        # Step 6: Save the credentials
        print(f"\n💾 Step 4: Saving account credentials ({'to database' if USE_DATABASE else 'to file'})...")
        
        if USE_DATABASE:
            upsert_platform_account(
                platform="instagram",
                page_id=ig_user_id,
                access_token=page_token,  # Use page token for Instagram API calls
                display_name=ig_username
            )
        else:
            success = save_instagram_token({
                "access_token": page_token,  # Use page token for Instagram API calls
                "ig_user_id": ig_user_id,
                "username": ig_username
            })
            if not success:
                print("❌ Failed to save token to file")
                return
        
        print("\n🎉 Setup complete! You can now post to Instagram via the dashboard.")
        print("\n💡 Next steps:")
        print("   1. Run the dashboard: streamlit run app/ui/dashboard.py")
        print("   2. Select Instagram as your platform")
        print("   3. Create and post content!")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Make sure your Instagram account is a Business or Creator account")
        print("   - Check that your app credentials are correct in .env")
        print("   - Verify your redirect URI matches exactly")

if __name__ == "__main__":
    main() 