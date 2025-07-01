# Pinterest Authentication Setup Guide

This guide walks you through setting up Pinterest OAuth2 authentication for the Social Media Scheduler, enabling you to post pins to your Pinterest boards as part of multi-platform posting.

---

## Prerequisites

### 1. Pinterest Developer Account
- You need a Pinterest Business account or Personal account
- Access to Pinterest Developer Platform: https://developers.pinterest.com/
- App approval from Pinterest (required for production use)

### 2. Pinterest App Creation
1. Go to [Pinterest Developers](https://developers.pinterest.com/)
2. Sign in with your Pinterest account
3. Click "Create app" or "My apps" → "Create app"
4. Fill in app details:
   - **App name**: "Social Media Scheduler" (or your preferred name)
   - **App description**: "Multi-platform social media scheduling tool"
   - **App website**: Your website URL (can be localhost for development)
   - **Redirect URI**: `http://localhost:8080/pinterest_callback`

### 3. Required Pinterest Scopes
Ensure your app requests these scopes:
- `boards:read` - Read user's boards
- `boards:write` - Create and modify boards
- `pins:read` - Read user's pins
- `pins:write` - Create and modify pins
- `user_accounts:read` - Read user account information

---

## Environment Configuration

### 1. Update .env File
Add these Pinterest configuration variables to your `.env` file:

```env
# Pinterest API Configuration
PINTEREST_CLIENT_ID=your_client_id_here
PINTEREST_CLIENT_SECRET=your_client_secret_here
PINTEREST_REDIRECT_URI=http://localhost:8080/pinterest_callback
PINTEREST_ACCESS_TOKEN=
PINTEREST_REFRESH_TOKEN=
```

### 2. Get Pinterest App Credentials
1. In your Pinterest app dashboard, go to "App settings"
2. Copy the **App ID** → use as `PINTEREST_CLIENT_ID`
3. Copy the **App secret** → use as `PINTEREST_CLIENT_SECRET`
4. Verify the **Redirect URI** matches your `.env` setting

---

## Authentication Setup

### 1. Run Pinterest Setup Script
```bash
python scripts/pinterest_setup.py
```

### 2. Follow the Interactive Process
The script will:
1. **Validate Configuration**: Check your Pinterest app credentials
2. **Open Browser**: Launch Pinterest OAuth2 authorization page
3. **User Authorization**: You'll authorize the app to access your Pinterest account
4. **Callback Handling**: Pinterest redirects to your callback URL with authorization code
5. **Token Exchange**: Script exchanges code for access and refresh tokens
6. **Account Discovery**: Retrieves your Pinterest account info and boards
7. **Credential Storage**: Saves tokens to database or file (based on `USE_DATABASE` setting)

### 3. Authorization Flow Details
1. **Browser Opens**: Pinterest authorization page
2. **Grant Permissions**: Click "Allow" to authorize the app
3. **Redirect**: Pinterest redirects to `http://localhost:8080/pinterest_callback?code=...`
4. **Copy URL**: Copy the complete callback URL from your browser
5. **Paste in Terminal**: The script will ask for this URL
6. **Automatic Processing**: Script handles token exchange and account setup

---

## Verification

### 1. Check Connection Status
After setup, verify the connection:
```bash
python -c "from app.platforms.pinterest import test_pinterest_connection; test_pinterest_connection()"
```

### 2. Expected Output
```
✅ Pinterest connection successful
👤 User: your_username
📌 Boards: 5 found
   - My First Board (12 pins)
   - Travel Inspiration (45 pins)
   - Recipe Ideas (23 pins)
```

### 3. Dashboard Verification
1. Run the main application: `python main.py`
2. In the dashboard sidebar, check "Platform Connections"
3. Pinterest should show: `🟢 Pinterest: Connected`
4. Should display: `Account: @your_username` and `Boards: X available`

---

## Pinterest-Specific Features

### 1. Board Management
- **Default Board**: Posts go to your first available board
- **Multiple Boards**: App detects all your boards automatically
- **Board Selection**: Uses the first public board by default

### 2. Pin Optimization
- **Image Requirement**: Pinterest works best with images
- **Optimal Dimensions**: Vertical images (2:3 ratio) perform best
- **Title Limits**: Pinterest titles are limited to 100 characters
- **Description Limits**: Descriptions are limited to 800 characters

### 3. Content Formatting
- **Title**: First line of your content becomes the pin title
- **Description**: Full content becomes the pin description
- **Media**: Uploaded images are attached to the pin
- **Link**: Optional website link can be added to pins

---

## Multi-Platform Integration

### 1. Platform Selection
- Pinterest appears in the platform checkbox list
- Status: `✅ Pinterest` when configured
- Can be combined with Facebook, Instagram, and other platforms

### 2. Batch Posting
- Select Pinterest along with other platforms
- Content is optimised for Pinterest's format automatically
- Media is uploaded and attached to pins
- Success/failure feedback is provided per platform

### 3. Smart Validation
- App shows "📌 Pinterest works best with images" when selected
- Recommends vertical image format for optimal performance
- Validates board availability before posting

---

## Troubleshooting

### Common Issues

#### 1. "No boards found" Error
**Problem**: Pinterest API returns empty boards list
**Solutions**:
- Ensure you have at least one board created on Pinterest
- Check that your boards are public or accessible
- Verify your app has `boards:read` permission

#### 2. "Media upload failed" Error
**Problem**: Image upload to Pinterest fails
**Solutions**:
- Check image format (PNG, JPG, GIF supported)
- Ensure image file size is under Pinterest limits
- Verify your app has `pins:write` permission

#### 3. "Authentication failed" Error
**Problem**: Pinterest API returns 401 Unauthorized
**Solutions**:
- Re-run `python scripts/pinterest_setup.py`
- Check that access token hasn't expired
- Verify Pinterest app credentials in `.env`

#### 4. "Permission denied" Error
**Problem**: Pinterest API returns 403 Forbidden
**Solutions**:
- Check your Pinterest app has all required scopes
- Ensure your Pinterest app is approved for production use
- Verify your account has necessary permissions

### Debug Information

#### 1. Check Stored Credentials
```bash
# For file-based storage
cat app/secure/pinterest_token.json

# For database storage
# Check platform_accounts table for pinterest entries
```

#### 2. Test API Connection
```bash
python -c "
from app.platforms.pinterest import get_pinterest_user_info, load_pinterest_credentials
creds = load_pinterest_credentials()
if creds:
    info = get_pinterest_user_info(creds['access_token'])
    print(f'User: {info}')
else:
    print('No credentials found')
"
```

#### 3. Manual Token Refresh
If tokens expire, the app will automatically attempt to refresh them using the refresh token.

---

## Pinterest API Limits

### 1. Rate Limits
- Pinterest API has rate limits per app and per user
- Standard limits: 1000 requests per hour per access token
- The app handles rate limiting gracefully with error messages

### 2. Content Limits
- **Pin Title**: 100 characters maximum
- **Pin Description**: 800 characters maximum
- **Image Size**: Maximum 32MB per image
- **Supported Formats**: PNG, JPG, GIF

### 3. Account Requirements
- Pinterest Business accounts have higher limits
- Personal accounts can be used but with reduced functionality
- Some features require Pinterest app approval

---

## Security Notes

### 1. Token Storage
- Access tokens are stored securely (encrypted file or database)
- Refresh tokens allow automatic token renewal
- Tokens are never logged or displayed in plain text

### 2. Scope Limitations
- App only requests minimum necessary permissions
- No access to private boards unless explicitly granted
- Cannot perform actions outside granted scopes

### 3. Data Privacy
- App only accesses Pinterest data needed for posting
- No data is shared with third parties
- User can revoke access anytime through Pinterest settings

---

## Next Steps

After successful Pinterest setup:

1. **Test Posting**: Create a test post with an image to verify functionality
2. **Multi-Platform**: Combine Pinterest with Facebook and Instagram for comprehensive posting
3. **Content Strategy**: Optimise content for Pinterest's visual format
4. **Board Organization**: Consider creating dedicated boards for scheduled content

For additional help, check the main README.md or create an issue in the project repository. 