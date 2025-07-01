
# Facebook Authentication Setup Guide

This guide explains how to configure and test Facebook authentication for the Social Media Scheduler. It covers the process of creating a Facebook App, requesting permissions, and storing access tokens either in a secure file or in the database, depending on your configuration.

---

## Step 1: Create a Facebook Developer Account

1. Visit [Meta for Developers](https://developers.facebook.com/)
2. Log in with your Facebook account and accept the developer terms
3. Click on **My Apps** > **Create App**
4. Choose **Business** as the app type and click **Next**
5. Enter an app name (e.g., "Story Chamber Scheduler") and your email address
6. Click **Create App**

---

## Step 2: Configure OAuth Settings

1. In your app dashboard, go to **Facebook Login** > **Settings**
2. Enable the following:
   - Client OAuth Login: ✅ Enabled
   - Web OAuth Login: ✅ Enabled
   - Use Strict Mode for Redirect URIs: ✅ Enabled
   - Enforce HTTPS: ❌ (optional for local development)
3. Add the following to **Valid OAuth Redirect URIs**:
   ```
   http://localhost:8080/callback
   ```

---

## Step 3: Enable Required Permissions

Go to **App Review → Permissions and Features**, and set the following permissions to **"Ready for Testing"**:

- `pages_manage_posts`
- `pages_read_engagement`
- `pages_show_list`
- `public_profile`
- `email` (optional)

Ensure your Facebook account is listed under **Roles → Developers**.

---

## Step 4: Configure Environment Variables

Create a `.env` file in the root of your project and add the following:

```env
FACEBOOK_CLIENT_ID=your_app_id
FACEBOOK_CLIENT_SECRET=your_app_secret
FACEBOOK_REDIRECT_URI=http://localhost:8080/callback
FACEBOOK_ACCESS_TOKEN=
USE_DATABASE=true
```

If `USE_DATABASE` is set to `true`, tokens will be stored in your MySQL database. If set to `false`, tokens will be saved in `app/secure/facebook_token.json`.

---

## Step 5: Install Required Packages

Ensure you’ve installed the following:

```bash
pip install requests requests_oauthlib python-dotenv mysql-connector-python
```

---

## Step 6: Run the Facebook Login Flow

Use the setup script to begin the login process:

```bash
python scripts/facebook_setup.py
```

1. Visit the login URL printed in your terminal
2. Authorise the app with your Facebook account
3. Copy and paste the full redirect URL back into the terminal

---

## Step 7: Fetch and Store Facebook Pages

Once authorised, the script will:

- Fetch the list of Pages you manage
- For each Page:
  - Store the access token and metadata in the database if `USE_DATABASE=true`
  - Or save them in a secure JSON file if `USE_DATABASE=false`

---

## Step 8: Schedule or Post Content

You can now use these tokens to publish posts:

### To schedule posts using the database:
1. Insert a scheduled post into the `posts` table with `account_id` referencing the desired Page
2. Run the scheduler:
   ```bash
   python post_scheduler.py
   ```

### To test immediate posting manually:
Use the `post_to_page()` function from your Facebook API module.

---

## Verifying the Setup

- Check your `platform_accounts` table in MySQL to confirm tokens are saved
- Or check for the `facebook_token.json` file in `app/secure/`
- Use the [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/) to inspect and verify token scopes

---

## Troubleshooting

- Ensure your account has **Full Control** access to the Facebook Page
- Make sure all required permissions are set to **Ready for Testing**
- Re-run the login script after making permission changes
- Ensure your `.env` and `config.py` are consistent with your setup

---

This completes the Facebook authentication setup for the Social Media Scheduler.
