# Tumblr Authentication Setup Guide

This guide will help you set up Tumblr OAuth 1.0a authentication for the Social Media Scheduler.

## Prerequisites

1. **Tumblr Account**: You need an active Tumblr account
2. **Tumblr Developer Application**: You need to create a Tumblr app in the developer portal

## Step 1: Create a Tumblr Application

1. Go to the [Tumblr Developer Portal](https://www.tumblr.com/oauth/apps)
2. Click "Register Application"
3. Fill in your application details:
   - **Application Name**: Choose a descriptive name (e.g., "My Social Media Scheduler")
   - **Application Website**: Your website or app URL
   - **Application Description**: Brief description of your app
   - **Administrative Contact Email**: Your email address
   - **Default Callback URL**: `http://localhost:8080/callback/tumblr` (or your custom callback URL)

4. Accept the Terms of Service
5. Click "Register"

## Step 2: Get Your Application Credentials

After creating your app, you'll get:
- **OAuth Consumer Key** (Client ID)
- **OAuth Consumer Secret** (Client Secret)

⚠️ **Important**: Keep these credentials secure and never share them publicly.

## Step 3: Configure Environment Variables

Add the following to your `.env` file:

```env
# Tumblr OAuth 1.0a Configuration
TUMBLR_CLIENT_ID=your_consumer_key_here
TUMBLR_CLIENT_SECRET=your_consumer_secret_here
TUMBLR_REDIRECT_URI=http://localhost:8080/callback/tumblr
```

## Step 4: Run the Authentication Setup

Execute the Tumblr setup script:

```bash
python scripts/tumblr_setup.py
```

The script will:
1. ✅ Validate your environment variables
2. 🔗 Generate an authorization URL
3. 🌐 Open your browser to the Tumblr authorization page
4. 📝 Prompt you to paste the callback URL
5. 🔄 Exchange the verifier for access tokens
6. 👤 Retrieve your user information
7. 💾 Save your credentials securely
8. 🧪 Test the connection

## Step 5: Authorize Your Application

1. The script will open Tumblr's authorization page in your browser
2. Log in to Tumblr if not already logged in
3. Review the permissions your app is requesting:
   - **Write**: Create and edit posts
   - **Read**: Access your blog information
4. Click "Allow" to authorize your application
5. You'll be redirected to your callback URL
6. Copy the full callback URL and paste it into the script

## Verification

After successful setup, you should see:
- ✅ **Connection Status**: Shows as "Connected" in the dashboard
- 👤 **Account Info**: Your Tumblr username
- 📝 **Blog Info**: Your primary blog name and title
- 📊 **Stats**: Follower count, post count, and total blogs

## Tumblr Features

### Supported Post Types
- **Text Posts**: Rich text content with titles
- **Photo Posts**: Images with captions
- **Video Posts**: Video content with captions
- **Link Posts**: Shared links with descriptions

### Content Guidelines
- **Title Length**: Up to 100 characters for text posts
- **Caption Length**: Up to 800 characters
- **Media Support**: JPG, PNG, GIF images; MP4, MOV videos
- **Tags**: Automatically adds "social-media-scheduler" tag

### Multi-Blog Support
- Automatically posts to your primary blog
- Supports multiple blogs under one account
- Blog selection handled automatically

## Troubleshooting

### Common Issues

**❌ "Missing required environment variables"**
- Ensure all three environment variables are set in your `.env` file
- Check for typos in variable names
- Restart the application after updating `.env`

**❌ "Failed to generate authorization URL"**
- Verify your Consumer Key and Secret are correct
- Check that your Tumblr app is properly configured
- Ensure your callback URL matches exactly

**❌ "oauth_verifier not found in URL"**
- Make sure you copied the complete callback URL
- The URL should contain both `oauth_token` and `oauth_verifier` parameters
- Try the authorization process again

**❌ "Failed to exchange tokens"**
- Ensure you authorized the application in the browser
- Check that the oauth_token matches between steps
- Verify your Consumer Secret is correct

**❌ "Connection test failed"**
- Your tokens may have been revoked
- Check your Tumblr app settings
- Re-run the setup script to get new tokens

### API Limits

Tumblr has the following limits:
- **Posts per day**: 250 posts per blog per day
- **Follows per hour**: 200 follows per hour
- **Rate limiting**: Varies by endpoint, generally generous for posting

### Token Management

- **Token Expiration**: OAuth 1.0a tokens don't expire automatically
- **Token Revocation**: Users can revoke access from their Tumblr settings
- **Token Refresh**: Not needed for OAuth 1.0a (unlike OAuth 2.0)

## Security Notes

- 🔒 Your OAuth tokens are stored securely (database or encrypted files)
- 🔑 Consumer Key and Secret should never be shared
- 🚫 Tokens can be revoked from Tumblr account settings
- 🔄 Re-run setup script if tokens are compromised

## Multi-Platform Integration

Tumblr integrates seamlessly with other platforms:
- ✅ **Batch Posting**: Post to Tumblr + Facebook + Instagram + Pinterest simultaneously
- 📅 **Scheduling**: Schedule posts for optimal Tumblr engagement times
- 🤖 **AI Enhancement**: Use AI to optimise content for Tumblr's creative community
- 📊 **Unified Dashboard**: Manage all platforms from one interface

## Next Steps

After successful setup:
1. 🚀 **Test Posting**: Create a test post to verify everything works
2. 📱 **Dashboard**: Use the main dashboard to create and schedule posts
3. 🎨 **Content**: Tumblr works great with creative, visual content
4. 📈 **Analytics**: Monitor your post performance

## Support

If you encounter issues:
1. Check the [Tumblr API Documentation](https://www.tumblr.com/docs/en/api/v2)
2. Review your app settings in the [Developer Portal](https://www.tumblr.com/oauth/apps)
3. Ensure your callback URL is correctly configured
4. Try regenerating your Consumer Key and Secret if needed

---

**Happy Tumbling!** 🎨✨ 