# TikTok Authentication Setup Guide

This guide will walk you through setting up TikTok API access for the Social Media Scheduler.

## Overview

TikTok uses OAuth 2.0 for authentication. You'll need to:
1. Create a TikTok Developer Account
2. Create a TikTok App
3. Configure OAuth settings
4. Get your app credentials
5. Run the setup script

## Prerequisites

- A TikTok account
- A TikTok Developer Account
- Content Posting API access (may require approval)

## Step 1: Create a TikTok Developer Account

1. Go to [TikTok for Developers](https://developers.tiktok.com/)
2. Click "Get Started" or "Log in"
3. Sign in with your TikTok account
4. Complete the developer account setup process

## Step 2: Create a TikTok App

1. In the TikTok Developer Console, click "Create an App"
2. Fill in the basic information:
   - **App Name**: Your application name (e.g., "Social Media Scheduler")
   - **App Description**: Brief description of your app
   - **Category**: Choose the most appropriate category
   - **Website URL**: Your website URL (required)

3. Set up Terms of Service and Privacy Policy URLs (required)
4. Choose your platform: **Web**

## Step 3: Add Products to Your App

1. In your app dashboard, click "Add products"
2. Add these products:
   - **Login Kit**: For user authentication
   - **Content Posting API**: For posting videos (may require approval)

## Step 4: Configure OAuth Settings

### Set Redirect URI
1. In the Login Kit section, find "Redirect URI"
2. Add your redirect URI (e.g., `http://localhost:3000/callback`)
3. Make sure this exactly matches what you'll put in your `.env` file

### Set Required Scopes
1. In the "Scopes" section, enable these scopes:
   - `user.info.basic`: Basic user information
   - `user.info.profile`: User profile information
   - `video.list`: Access to user's videos
   - `video.upload`: Upload videos
   - `video.publish`: Publish videos directly (requires Direct Post approval)

## Step 5: Get Your App Credentials

1. In your app dashboard, go to "Basic Information"
2. Find and copy:
   - **Client Key** (this is your Client ID)
   - **Client Secret**

## Step 6: Set Up Environment Variables

Create or update your `.env` file with:

```env
# TikTok API Configuration
TIKTOK_CLIENT_ID=your_client_key_here
TIKTOK_CLIENT_SECRET=your_client_secret_here
TIKTOK_REDIRECT_URI=http://localhost:3000/callback
```

## Step 7: Request App Review (If Required)

For production use or Direct Post functionality:

1. In your app dashboard, go to "App Review"
2. Submit your app for review with:
   - A detailed description of how you'll use the API
   - Demo videos showing the integration
   - All required information

**Note**: TikTok may require app review for Content Posting API access.

## Step 8: Run the Setup Script

Once your app is configured:

```bash
python scripts/tiktok_setup.py
```

The script will:
1. Generate an authorization URL
2. Guide you through the login process
3. Save your access token securely
4. Verify the connection

## Important Notes

### Rate Limits
- **Video uploads**: 2 videos per minute, 20 videos per day
- **API calls**: Various limits depending on the endpoint

### Content Requirements
- **Video format**: MP4 recommended
- **Video size**: Up to 500MB
- **Duration**: 15 seconds to 10 minutes
- **Resolution**: Minimum 540x960, maximum 1920x1080

### Direct Post vs Draft
- **Draft mode**: Videos are saved as drafts for manual publishing
- **Direct Post**: Videos are published immediately (requires approval)

## Troubleshooting

### Common Issues

**"Invalid redirect URI"**
- Ensure your redirect URI in the app matches exactly what's in your `.env` file
- Check for trailing slashes or case sensitivity

**"Insufficient permissions"**
- Verify all required scopes are enabled in your app
- Check if your app needs review for Content Posting API access

**"App not approved"**
- Some features require app review
- Submit your app for review with proper documentation

**"Token expired"**
- TikTok access tokens may expire
- Re-run the setup script to get a new token

### Debug Steps

1. Check your `.env` file configuration
2. Verify your app credentials in the TikTok Developer Console
3. Ensure your redirect URI is accessible
4. Check the app review status if using advanced features

## Environment Variables Reference

```env
# Required
TIKTOK_CLIENT_ID=your_client_key
TIKTOK_CLIENT_SECRET=your_client_secret
TIKTOK_REDIRECT_URI=your_redirect_uri

# Optional (for existing tokens)
TIKTOK_ACCESS_TOKEN=your_existing_token
```

## Testing Your Setup

After running the setup script, test your configuration:

1. Run the main application: `python main.py`
2. Check that TikTok appears as an available platform
3. Try uploading a test video
4. Verify the post appears in your TikTok account

## Security Best Practices

- Never commit your `.env` file to version control
- Store credentials securely
- Use environment variables for sensitive data
- Regularly rotate access tokens
- Monitor your app's usage in the TikTok Developer Console

## Additional Resources

- [TikTok for Developers Documentation](https://developers.tiktok.com/)
- [TikTok API Reference](https://developers.tiktok.com/doc)
- [TikTok Content Posting API](https://developers.tiktok.com/doc/content-posting-api-overview)
- [TikTok App Review Guidelines](https://developers.tiktok.com/doc/app-review-guidelines)

---

**Need help?** Check the [troubleshooting section](../README.md#troubleshooting) or open an issue on GitHub. 