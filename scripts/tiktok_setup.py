#!/usr/bin/env python3
"""
TikTok Authentication Setup

This script handles TikTok OAuth2 authentication and retrieves user access tokens.
Stores them securely (either in database or JSON file).

Usage:
    python scripts/tiktok_setup.py
"""

import json
import os
import sys
from pathlib import Path

# Add the parent directory to the path to import app modules
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.auth.tiktok_auth import get_tiktok_login_url, fetch_tiktok_token
from app.platforms.tiktok import get_user_info
from app.config import USE_DATABASE, TIKTOK_ACCESS_TOKEN

if USE_DATABASE:
    from app.db.database import execute_query

def upsert_platform_account(platform, page_id, access_token, display_name):
    """
    Insert or update platform account in database.
    
    Args:
        platform (str): Platform name (e.g., 'tiktok')
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

def save_tiktok_token(data: dict) -> bool:
    """
    Save TikTok token data to JSON file.
    
    Args:
        data (dict): Token data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        secure_dir = Path(__file__).parent.parent / "app" / "secure"
        secure_dir.mkdir(exist_ok=True)

        token_file = secure_dir / "tiktok_token.json"
        with open(token_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✅ TikTok tokens saved to: {token_file}")
        return True

    except Exception as e:
        print(f"❌ Error saving TikTok tokens: {e}")
        return False

def main():
    """Main function to handle TikTok authentication and token fetching."""
    
    print("🔗 TikTok Token Setup")
    print("=" * 40)
    print(f"📊 Storage mode: {'Database' if USE_DATABASE else 'File-based'}")

    # Check if we already have a token in environment
    if TIKTOK_ACCESS_TOKEN:
        print("🔑 Using existing access token from environment...")
        access_token = TIKTOK_ACCESS_TOKEN
        try:
            user_info = get_user_info(access_token)
            open_id = user_info.get('open_id')
            display_name = user_info.get('display_name', 'TikTok User')

            if not open_id:
                print("❌ Failed to retrieve TikTok user information with existing token.")
                print("💡 The token may be expired. Let's get a new one...")
            else:
                print(f"📊 Found TikTok User: {display_name} (ID: {open_id})")
                
                # Save the credentials
                if USE_DATABASE:
                    upsert_platform_account(
                        platform="tiktok",
                        page_id=open_id,
                        access_token=access_token,
                        display_name=display_name
                    )
                else:
                    save_tiktok_token({
                        "access_token": access_token,
                        "open_id": open_id,
                        "display_name": display_name
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
        auth_url = get_tiktok_login_url()
        print("\n🌐 Please go to this URL and log in to TikTok:")
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
        token_data = fetch_tiktok_token(redirect_response)
        
        access_token = token_data.get('access_token')
        
        if not access_token:
            print("❌ Failed to get access token")
            print(f"Response: {token_data}")
            return
            
        print("✅ Access token obtained")
        
        # Step 4: Get user info
        print("\n📄 Step 3: Fetching TikTok user information...")
        user_info = get_user_info(access_token)
        
        open_id = user_info.get('open_id')
        display_name = user_info.get('display_name', 'TikTok User')
        
        if not open_id:
            print("❌ Failed to retrieve TikTok user information.")
            print(f"Response: {user_info}")
            return
        
        # Step 5: Display user info
        print(f"\n📊 Found TikTok User:")
        print(f"   Display Name: {display_name}")
        print(f"   Open ID: {open_id}")
        
        # Step 6: Save the credentials
        print(f"\n💾 Step 4: Saving account credentials ({'to database' if USE_DATABASE else 'to file'})...")
        
        if USE_DATABASE:
            upsert_platform_account(
                platform="tiktok",
                page_id=open_id,
                access_token=access_token,
                display_name=display_name
            )
        else:
            success = save_tiktok_token({
                "access_token": access_token,
                "open_id": open_id,
                "display_name": display_name
            })
            if not success:
                print("❌ Failed to save token to file")
                return
        
        print("\n🎉 Setup complete! You can now post to TikTok via the dashboard.")
        print("\n💡 Next steps:")
        print("   1. Run the dashboard: python main.py")
        print("   2. Select TikTok as your platform")
        print("   3. Upload videos and start posting!")
        print("\n⚠️  Important notes:")
        print("   - TikTok primarily supports video content")
        print("   - Rate limits: 2 videos per minute, 20 videos per day")
        print("   - Videos must be in MP4 format")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Make sure your TikTok app credentials are correct in .env")
        print("   - Verify your redirect URI matches exactly")
        print("   - Check that your app has the required scopes enabled")
        print("   - For business accounts, ensure you have the Content Posting API enabled")

if __name__ == "__main__":
    main()
