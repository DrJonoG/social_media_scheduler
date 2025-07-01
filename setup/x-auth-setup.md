# X (Twitter) Authentication Setup Guide

This guide will walk you through setting up OAuth 2.0 authentication for X (formerly Twitter) to enable posting through the Social Media Scheduler.

## Overview

X uses **OAuth 2.0 Authorization Code Flow with PKCE** for enhanced security. This modern authentication method provides:
- Enhanced security with PKCE (Proof Key for Code Exchange)
- Automatic token refresh capabilities
- Fine-grained permission scopes
- Support for both confidential and public clients

## Prerequisites

Before you begin, make sure you have:

1. **X Developer Account** - Apply at [developer.x.com](https://developer.x.com/)
2. **Approved X App** - Must be approved for posting capabilities
3. **OAuth 2.0 Enabled** - In your app settings
4. **Python Environment** - With required dependencies installed

## Step 1: Create X Developer Account

### Apply for Developer Access
1. Visit [developer.x.com](https://developer.x.com/)
2. Click "Apply for a developer account"
3. Fill out the application form with:
   - Your intended use case
   - How you plan to use the X API
   - Whether you'll display X content to users
4. Wait for approval (can take several days)

### Account Requirements
- Valid X account (not suspended)
- Phone number verification
- Clear use case description
- Compliance with X Developer Policy

## Step 2: Create X App

### Create New App
1. Log into the [X Developer Portal](https://developer.x.com/en/portal/dashboard)
2. Navigate to "Projects & Apps"
3. Click "Create App"
4. Choose app type:
   - **Web App** (recommended for this use case)
   - **Native App** (for mobile/desktop apps)
   - **Single Page App** (for browser-only apps)

### App Configuration
1. **App Name**: Choose a unique name for your app
2. **App Description**: Describe your social media scheduler
3. **Website URL**: Your website or GitHub repository
4. **Callback URL**: Set to `http://localhost:8080/x_callback`
5. **Terms of Service**: Link to your terms (if applicable)
6. **Privacy Policy**: Link to your privacy policy (if applicable)

### Enable OAuth 2.0
1. In your app settings, go to "Authentication settings"
2. Enable **OAuth 2.0**
3. Set app type to **Web App** (for confidential client)
4. Configure callback URLs:
   - `http://localhost:8080/x_callback` (for local testing)
   - Your production callback URL (if applicable)

## Step 3: Configure App Permissions

### Required Scopes
Your app needs these permissions:
- **tweet.read** - Read tweets and user information
- **tweet.write** - Create and delete tweets
- **users.read** - Access user profile information
- **offline.access** - Maintain long-term access (refresh tokens)

### Optional Scopes
Depending on your needs:
- **follows.read** - Read following/followers lists
- **follows.write** - Follow/unfollow users
- **like.read** - Read liked tweets
- **like.write** - Like/unlike tweets

**Note**: Media uploads use OAuth 1.0a credentials, not OAuth 2.0 scopes

### Set App Permissions
1. Go to your app's "Permissions" tab
2. Select **Read and Write** permissions
3. Enable **Request email address from users** (optional)
4. Save changes

## Step 4: Get API Credentials

### OAuth 2.0 Credentials
1. Navigate to "Keys and tokens" tab
2. Find your **Client ID** (always visible)
3. Generate **Client Secret** (for confidential clients)
4. Copy both values securely

### Legacy Credentials (for Media Upload)
X requires OAuth 1.0a for media uploads via v1.1 API:
1. In "Keys and tokens", find:
   - **API Key** (Consumer Key)
   - **API Key Secret** (Consumer Secret)
2. Generate **Access Token and Secret**:
   - Click "Generate" under "Access Token and Secret"
   - **IMPORTANT**: Ensure permissions are set to **Read and Write** (NOT Read Only)
   - If tokens show "Read Only", regenerate them with Write permissions
   - Copy the generated tokens

## Step 5: Environment Configuration

### Update .env File
Add these variables to your `.env` file:

```bash
# X (Twitter) OAuth 2.0 Credentials
X_CLIENT_ID=your_client_id_here
X_CLIENT_SECRET=your_client_secret_here
X_REDIRECT_URI=http://localhost:8080/x_callback

# X (Twitter) OAuth 1.0a Credentials (for media upload)
X_API_KEY=your_api_key_here
X_API_SECRET=your_api_secret_here
X_ACCESS_TOKEN=your_access_token_here
X_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

### Security Notes
- Keep your Client Secret secure and never expose it publicly
- Use environment variables for all sensitive credentials
- Consider using different credentials for development and production
- Rotate credentials periodically for security

## Step 6: Run Authentication Setup

### Execute Setup Script
Run the X authentication setup script:

```bash
python scripts/x_setup.py
```

### Setup Process
The script will:
1. **Validate Configuration** - Check your environment variables
2. **Generate Auth URL** - Create OAuth 2.0 authorization URL with PKCE
3. **Open Browser** - Redirect you to X for authorization
4. **Handle Callback** - Process the authorization code
5. **Exchange Tokens** - Get access and refresh tokens
6. **Get User Info** - Retrieve your account information
7. **Save Credentials** - Store tokens securely
8. **Test Connection** - Verify everything works

### Authorization Flow
1. Browser opens to X authorization page
2. Log in with your X account
3. Review and approve permissions
4. Copy the full callback URL from your browser
5. Paste it into the setup script
6. Wait for token exchange and verification

## Step 7: Verify Setup

### Test Connection
The setup script automatically tests your connection. You should see:
- ✅ Configuration validated
- ✅ Authorization successful
- ✅ Tokens exchanged
- ✅ User information retrieved
- ✅ Connection test passed

### Manual Verification
You can also test manually:

```bash
python -c "
from app.platforms.x import test_x_connection
result = test_x_connection()
print('✅ Connected!' if result['success'] else f'❌ Error: {result[\"error\"]}')
"
```

## X API Features

### Posting Capabilities
- **Text Posts**: Up to 280 characters
- **Media Posts**: Images (JPEG, PNG, GIF) and videos (MP4, MOV)
- **Multiple Images**: Up to 4 images per tweet
- **Single Video**: One video per tweet (max 512MB)
- **Threads**: Multiple connected tweets (future feature)

### Content Guidelines
- **Character Limit**: 280 characters for text
- **Image Formats**: JPEG, PNG, GIF (max 5MB each)
- **Video Formats**: MP4, MOV (max 512MB)
- **Optimal Image Size**: 1200x675 pixels (16:9 ratio)
- **Video Length**: Up to 2 minutes and 20 seconds

### Rate Limits
- **Standard Account**: 300 tweets per hour
- **Verified Account**: 2,400 tweets per day
- **API Calls**: 900 requests per 15 minutes (OAuth 2.0)
- **Media Upload**: Separate rate limits apply

## Troubleshooting

### Common Issues

#### "Invalid Client ID"
- Verify `X_CLIENT_ID` in your .env file
- Ensure the Client ID is from the correct app
- Check for extra spaces or characters

#### "Redirect URI Mismatch"
- Verify callback URL in app settings matches `X_REDIRECT_URI`
- Ensure exact match (including protocol and port)
- Check for trailing slashes

#### "Insufficient Permissions"
- Verify app has "Read and Write" permissions
- Check that required scopes are enabled
- Regenerate tokens if permissions changed

#### "Token Expired"
- Access tokens expire in 2 hours by default
- Refresh tokens allow automatic renewal
- Re-run setup script if refresh fails

#### "Media Upload Failed"
- **Most Common**: Check if Access Token was created with "Read Only" permissions
  - Regenerate Access Token and Secret with "Read and Write" permissions
- Verify OAuth 1.0a credentials are correct
- Check file format and size limits
- Ensure media file is accessible

### Advanced Troubleshooting

#### Debug Mode
Enable debug logging:
```bash
export X_DEBUG=true
python scripts/x_setup.py
```

#### Manual Token Refresh
```python
from app.auth.x_auth import refresh_access_token
new_tokens = refresh_access_token("your_refresh_token")
```

#### Clear Stored Credentials
```bash
# Remove stored credentials
rm data/credentials/x_credentials.json
# Or clear database entry
python -c "
from app.db.database import execute_query
execute_query('DELETE FROM social_tokens WHERE platform = \"x\"')
"
```

## Security Best Practices

### Credential Management
- Never commit credentials to version control
- Use environment variables for all secrets
- Implement credential rotation policies
- Monitor for unauthorized access

### App Security
- Enable app-only authentication when possible
- Use HTTPS for all production callbacks
- Implement proper error handling
- Log security events appropriately

### User Privacy
- Only request necessary permissions
- Clearly communicate data usage
- Provide opt-out mechanisms
- Follow data protection regulations

## Multi-Platform Integration

### Scheduler Integration
Once configured, X works seamlessly with other platforms:
- **Unified Interface**: Single dashboard for all platforms
- **Batch Posting**: Post to X and other platforms simultaneously
- **Scheduled Posts**: Queue posts for optimal timing
- **Media Handling**: Automatic format optimization

### Content Optimization
- **Character Counting**: Real-time character limit tracking
- **Media Validation**: Automatic format and size checking
- **Hashtag Integration**: Smart hashtag suggestions
- **Thread Planning**: Future support for tweet threads

## Support and Resources

### Official Documentation
- [X API Documentation](https://docs.x.com/)
- [OAuth 2.0 Guide](https://docs.x.com/resources/fundamentals/authentication/oauth-2-0)
- [Rate Limits](https://docs.x.com/resources/fundamentals/rate-limits)
- [Developer Policy](https://developer.x.com/en/developer-terms/policy)

### Community Support
- [X Developer Community](https://twittercommunity.com/)
- [GitHub Issues](https://github.com/your-repo/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/twitter-api)

### Getting Help
If you encounter issues:
1. Check this troubleshooting guide
2. Review X API documentation
3. Search community forums
4. Create a GitHub issue with details

## Next Steps

After successful setup:
1. ✅ X is ready for use in the scheduler
2. 🚀 Launch the main application: `python main.py`
3. 📝 Select X in platform selection
4. 🎯 Create and schedule your first post
5. 📊 Monitor posting analytics and performance

Your X integration is now complete and ready for professional social media management! 