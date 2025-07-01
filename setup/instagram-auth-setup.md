# Instagram Authentication Setup Guide

This guide explains how to configure and test Instagram Business Login authentication for the Social Media Scheduler. It covers the process of creating an Instagram App, requesting permissions, and storing access tokens either in a secure file or in the database, depending on your configuration.

---

## Step 1: Create a Meta Developer Account

1. Visit [Meta for Developers](https://developers.facebook.com/)
2. Log in with your Facebook account and accept the developer terms
3. Click on **My Apps** > **Create App**
4. Choose **Business** as the app type and click **Next**
5. Enter an app name (e.g., "Story Chamber Instagram Scheduler") and your email address
6. Click **Create App**

---

## Step 2: Add Instagram Product

1. In your app dashboard, go to **Products** section on the left
2. Find **Instagram API with Instagram Login** and click **Set up**
3. Follow the setup wizard to configure Instagram API with Instagram Login
4. Complete the basic setup requirements

---

## Step 3: Configure Instagram Business Login Settings

1. In your app dashboard, go to **Instagram** > **API setup with Instagram login**
2. Complete **Step 3: Set up Instagram business login**
3. In the **Business login settings** section:
   - Note your **Instagram App ID**
   - Note your **Instagram App Secret**
   - Add valid OAuth redirect URIs:
     ```
     http://localhost:8080/ig_callback
     ```

---

## Step 4: Configure Required Permissions

The Instagram Business Login API requires specific scopes. Set the following permissions:

- `instagram_basic` - Required for basic account information
- `instagram_content_publish` - For posting content
- `pages_show_list` - To access your Facebook pages
- `pages_read_engagement` - To read page data
- `pages_manage_posts` - To post on behalf of your page

**Note:** These permissions may require App Review for production use with accounts you don't own.

---

## Step 5: Configure Environment Variables

Create or update your `.env` file in the root of your project and add the following:

```env
INSTAGRAM_CLIENT_ID=your_instagram_app_id
INSTAGRAM_CLIENT_SECRET=your_instagram_app_secret
INSTAGRAM_REDIRECT_URI=http://localhost:8080/ig_callback
INSTAGRAM_ACCESS_TOKEN=
USE_DATABASE=true
```

If `USE_DATABASE` is set to `true`, tokens will be stored in your MySQL database. If set to `false`, tokens will be saved in `app/secure/instagram_token.json`.

---

## Step 6: Instagram Account Requirements

**Important:** Your Instagram account must be:
- A **Business Account** or **Creator Account** (not a personal account)
- **Linked to a Facebook Page** that you have admin access to
- Have all necessary permissions granted during the OAuth flow

To set this up:
1. **Convert to Business Account:**
   - Open Instagram mobile app
   - Go to Settings > Account > Switch to Professional Account
   - Choose Business or Creator

2. **Link to Facebook Page:**
   - Go to your Facebook page settings
   - Navigate to Instagram > Connect Account
   - Follow the prompts to link your Instagram Business account
   - Ensure you have admin access to the Facebook page

**Note:** The Instagram Business API works through Facebook's Graph API, so you need both a Facebook page and a linked Instagram Business account.

---

## Step 7: Install Required Packages

Ensure you've installed the following:

```bash
pip install requests requests_oauthlib python-dotenv mysql-connector-python
```

---

## Step 8: Run the Instagram Login Flow

Use the setup script to begin the login process:

```bash
python scripts/instagram_setup.py
```

1. Visit the login URL printed in your terminal
2. Authorise the app with your Instagram Business account
3. Copy and paste the full redirect URL back into the terminal

---

## Step 9: Verify Token Storage

Once authorised, the script will:

- Fetch your Instagram Business Account information
- Store the access token and metadata:
  - In the database if `USE_DATABASE=true`
  - Or save them in a secure JSON file if `USE_DATABASE=false`

---

## Step 10: Test Instagram Posting

You can now use these tokens to publish posts:

### To schedule posts using the database:
1. Insert a scheduled post into the `posts` table with `account_id` referencing the Instagram account
2. Run the scheduler:
   ```bash
   python app/scheduler/post_scheduler.py
   ```

### To test immediate posting manually:
Use the `post_to_instagram()` function from your Instagram API module.

**Note:** Instagram requires media (images or videos) for all posts. Text-only posts are not supported.

---

## Verifying the Setup

- Check your `platform_accounts` table in MySQL to confirm tokens are saved
- Or check for the `instagram_token.json` file in `app/secure/`
- Test the connection by running the fetch script again

---

## Troubleshooting

### Common Issues:

1. **"Invalid redirect URI"**
   - Ensure the redirect URI in your .env matches exactly what's configured in the app dashboard
   - Check for trailing slashes

2. **"Account not found" or "Invalid user"**
   - Make sure your Instagram account is a Business or Creator account
   - Verify the account is properly linked to a Facebook Page
   - Ensure you have admin access to the Facebook page
   - Check that the Instagram account appears in your Facebook page settings

3. **Permission denied errors**
   - Ensure all required scopes are requested
   - Check that your app has the necessary permissions configured

4. **Token expired**
   - Instagram Business Login tokens are long-lived (60 days) but can expire
   - Re-run the setup script to get fresh tokens

### Advanced Troubleshooting:

- Use the [Instagram API Explorer](https://developers.facebook.com/tools/debug/accesstoken/) to test your tokens
- Check the [Instagram Platform Documentation](https://developers.facebook.com/docs/instagram-platform) for updates
- Ensure your app is not in Development Mode for production accounts

---

## Important Notes

- Instagram Business Login API is different from Instagram Basic Display API
- You cannot post to personal Instagram accounts - only Business/Creator accounts
- All Instagram posts require media (images or videos)
- Consider rate limits and API usage policies
- Tokens can be refreshed programmatically before expiration

---

This completes the Instagram authentication setup for the Social Media Scheduler. 