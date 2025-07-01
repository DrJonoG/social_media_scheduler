#!/usr/bin/env python3
"""
Tumblr OAuth 1.0a Setup Script

This script helps users authenticate with Tumblr using OAuth 1.0a
and saves the credentials for use in the social media scheduler.
"""

import os
import sys
import webbrowser
from urllib.parse import parse_qs, urlparse

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth.tumblr_auth import (
    generate_tumblr_auth_url,
    exchange_code_for_tokens,
    get_user_info,
    save_tumblr_credentials,
    validate_access_token
)
from app.platforms.tumblr import test_tumblr_connection

def check_environment():
    """Check if required environment variables are set."""
    required_vars = [
        'TUMBLR_CLIENT_ID',
        'TUMBLR_CLIENT_SECRET',
        'TUMBLR_REDIRECT_URI'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please add these to your .env file:")
        print("   TUMBLR_CLIENT_ID=your_consumer_key")
        print("   TUMBLR_CLIENT_SECRET=your_consumer_secret")
        print("   TUMBLR_REDIRECT_URI=your_callback_url")
        print("\n🔗 Get your Tumblr app credentials at: https://www.tumblr.com/oauth/apps")
        return False
    
    return True

def setup_tumblr_auth():
    """Main setup function for Tumblr OAuth 1.0a authentication."""
    print("🎨 Tumblr OAuth 1.0a Setup")
    print("=" * 50)
    
    # Check environment variables
    if not check_environment():
        return False
    
    print("✅ Environment variables found")
    
    # Display current configuration
    print(f"\n📋 Current Configuration:")
    print(f"   Consumer Key: {os.getenv('TUMBLR_CLIENT_ID')[:10]}...")
    print(f"   Consumer Secret: {'*' * 20}")
    print(f"   Redirect URI: {os.getenv('TUMBLR_REDIRECT_URI')}")
    
    try:
        # Step 1: Generate authorization URL
        print("\n🔗 Step 1: Getting authorization URL...")
        auth_data = generate_tumblr_auth_url()
        
        if not auth_data or 'auth_url' not in auth_data:
            print("❌ Failed to generate authorization URL")
            print("   Please check your TUMBLR_CLIENT_ID and TUMBLR_CLIENT_SECRET")
            return False
        
        auth_url = auth_data['auth_url']
        oauth_token = auth_data['oauth_token']
        oauth_token_secret = auth_data['oauth_token_secret']
        
        print(f"✅ Authorization URL generated")
        
        # Step 2: Open browser for user authorization
        print(f"\n🌐 Step 2: Opening authorization URL in browser...")
        print(f"   {auth_url}")
        
        try:
            webbrowser.open(auth_url)
            print("✅ Browser opened")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print("   Please manually open the URL above")
        
        # Step 3: Get authorization response
        print(f"\n🔑 Step 3: After authorizing, you'll be redirected to:")
        print(f"   {os.getenv('TUMBLR_REDIRECT_URI')}")
        print(f"\n   The URL will contain 'oauth_token' and 'oauth_verifier' parameters")
        
        while True:
            callback_url = input("\n📝 Please paste the full callback URL here: ").strip()
            
            if not callback_url:
                print("❌ Please provide the callback URL")
                continue
            
            # Parse the callback URL
            try:
                parsed_url = urlparse(callback_url)
                query_params = parse_qs(parsed_url.query)
                
                oauth_verifier = query_params.get('oauth_verifier', [None])[0]
                returned_oauth_token = query_params.get('oauth_token', [None])[0]
                
                if not oauth_verifier:
                    print("❌ oauth_verifier not found in URL. Please try again.")
                    continue
                
                if returned_oauth_token != oauth_token:
                    print("❌ oauth_token mismatch. Please try again.")
                    continue
                
                break
                
            except Exception as e:
                print(f"❌ Error parsing callback URL: {e}")
                continue
        
        # Step 4: Exchange for access tokens
        print(f"\n🔄 Step 4: Exchanging for access tokens...")
        
        token_data = exchange_code_for_tokens(
            oauth_token, 
            oauth_token_secret, 
            oauth_verifier
        )
        
        if not token_data or not token_data.get('success'):
            error_msg = token_data.get('error', 'Unknown error') if token_data else 'No response'
            print(f"❌ Failed to exchange tokens: {error_msg}")
            return False
        
        access_token = token_data['access_token']
        access_token_secret = token_data['access_token_secret']
        
        print("✅ Access tokens obtained")
        
        # Step 5: Validate tokens and get user info
        print(f"\n👤 Step 5: Getting user information...")
        
        if not validate_access_token(access_token, access_token_secret):
            print("❌ Failed to validate access tokens")
            return False
        
        user_info = get_user_info(access_token, access_token_secret)
        if not user_info:
            print("❌ Failed to get user information")
            return False
        
        print(f"✅ Connected to Tumblr successfully!")
        print(f"   Username: {user_info.get('username', 'Unknown')}")
        print(f"   Primary Blog: {user_info.get('blog_title', user_info.get('blog_name', 'Unknown'))}")
        print(f"   Blog URL: {user_info.get('blog_url', 'Unknown')}")
        print(f"   Total Blogs: {user_info.get('total_blogs', 0)}")
        print(f"   Followers: {user_info.get('followers', 0)}")
        print(f"   Posts: {user_info.get('posts', 0)}")
        
        # Step 6: Save credentials
        print(f"\n💾 Step 6: Saving credentials...")
        
        credentials = {
            'access_token': access_token,
            'access_token_secret': access_token_secret,
            'username': user_info.get('username'),
            'blog_name': user_info.get('blog_name'),
            'blog_title': user_info.get('blog_title'),
            'blog_url': user_info.get('blog_url')
        }
        
        if save_tumblr_credentials(credentials):
            print("✅ Credentials saved successfully")
        else:
            print("❌ Failed to save credentials")
            return False
        
        # Step 7: Test connection
        print(f"\n🧪 Step 7: Testing connection...")
        
        test_result = test_tumblr_connection()
        if test_result.get('success'):
            print("✅ Connection test successful!")
            print(f"   {test_result.get('message', '')}")
        else:
            print(f"❌ Connection test failed: {test_result.get('error', 'Unknown error')}")
            return False
        
        # Success message
        print(f"\n🎉 Tumblr Setup Complete!")
        print(f"=" * 50)
        print(f"✅ You can now use Tumblr in your social media scheduler")
        print(f"✅ Your credentials are saved and ready to use")
        print(f"✅ You can post to: {user_info.get('blog_title', user_info.get('blog_name', 'your blog'))}")
        
        return True
        
    except KeyboardInterrupt:
        print(f"\n\n❌ Setup cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        return False

def main():
    """Main entry point."""
    print("🚀 Social Media Scheduler - Tumblr Setup")
    print("=========================================")
    
    # Check if we're in the right directory
    if not os.path.exists('app'):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️  python-dotenv not found, assuming environment variables are set")
    except Exception as e:
        print(f"⚠️  Error loading .env file: {e}")
    
    # Run setup
    success = setup_tumblr_auth()
    
    if success:
        print(f"\n🎯 Next Steps:")
        print(f"   1. Run the main application: streamlit run app/ui/dashboard.py")
        print(f"   2. Select Tumblr as one of your platforms")
        print(f"   3. Create and schedule your posts!")
        
        print(f"\n📚 Tumblr Features:")
        print(f"   • Text posts with titles and rich formatting")
        print(f"   • Photo posts with captions")
        print(f"   • Video posts with captions")
        print(f"   • Link posts with descriptions")
        print(f"   • Support for multiple blogs")
        print(f"   • Automatic tag addition")
        
        print(f"\n🔒 Security Notes:")
        print(f"   • Your OAuth tokens are stored securely")
        print(f"   • Tokens don't expire but can be revoked from Tumblr settings")
        print(f"   • Keep your consumer key and secret confidential")
        
        sys.exit(0)
    else:
        print(f"\n❌ Setup failed. Please check the errors above and try again.")
        print(f"\n🔧 Troubleshooting:")
        print(f"   • Ensure your Tumblr app is properly configured")
        print(f"   • Check that your redirect URI matches exactly")
        print(f"   • Verify your consumer key and secret are correct")
        print(f"   • Make sure you authorized the application in the browser")
        
        sys.exit(1)

if __name__ == "__main__":
    main() 