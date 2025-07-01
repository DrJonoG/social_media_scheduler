# Database Structure

This document outlines the database schema for the Social Media Scheduler application.

## Required Tables

### Posts Table
The main table for storing scheduled posts:

```sql
CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50),
    content TEXT,
    media_path VARCHAR(255),
    scheduled_time DATETIME,
    status VARCHAR(20)
);
```

### Platform Accounts Table
Stores authentication credentials for social media platforms:

```sql
CREATE TABLE platform_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    page_id VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    access_token_secret TEXT,
    display_name VARCHAR(255),
    username VARCHAR(255),
    refresh_token TEXT,
    token_expires DATETIME,
    additional_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_platform_account (platform, page_id)
);
```

### Social Tokens Table
Stores OAuth 2.0 tokens for platforms like X (Twitter) that use separate token management:

```sql
CREATE TABLE social_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    user_id VARCHAR(255),
    username VARCHAR(255),
    expires_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_platform_user (platform, user_id)
);
```

## Setup Instructions

1. **Drop existing tables** (if you have them with wrong schema):
```sql
DROP TABLE IF EXISTS platform_accounts;
DROP TABLE IF EXISTS social_tokens;
DROP TABLE IF EXISTS posts;
```

2. **Create the tables** using the SQL statements above

3. **Update your `.env` file** with the database connection details:

```env
USE_DATABASE=TRUE
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=social_scheduler
```

## Alternative: SQLite

For development or single-user setups, you can use SQLite instead:

1. Set `USE_DATABASE=FALSE` in your `.env` file
2. The application will automatically create `data/posts.db` 
3. Credentials will be stored in encrypted JSON files in `app/secure/`

## Column Explanations

### platform_accounts table:
- `page_id`: Platform-specific account/page ID (Facebook page ID, Instagram user ID, etc.)
- `display_name`: Human-readable name (page name, username, etc.)
- `username`: Platform username (for platforms that use @username)
- `access_token`: OAuth access token for API calls
- `refresh_token`: OAuth refresh token (when available)

### social_tokens table:
- `user_id`: Platform-specific user ID
- `username`: Platform username
- Used specifically for X (Twitter) OAuth 2.0 with PKCE

## Usage Notes

- The `status` field in posts table uses values: 'scheduled', 'published', 'failed', 'draft'
- Platform credentials are automatically managed by the setup scripts
- Ensure proper backup procedures for production databases
- The application will automatically use the correct table based on the platform