# Authentication Module

This directory contains authentication components for social media platforms supported by the scheduler.

## Authentication Modules

- **`facebook_auth.py`** - Facebook OAuth2 authentication
  - Page access token management
  - OAuth2 flow with Facebook Graph API
  - Token storage and validation

- **`instagram_auth.py`** - Instagram Business authentication
  - Business account authentication via Facebook
  - Instagram-specific OAuth2 scopes
  - Account linking and verification

- **`pinterest_auth.py`** - Pinterest OAuth2 authentication
  - Board access and management
  - Pinterest API v5 OAuth2 flow
  - User and board information retrieval

- **`tumblr_auth.py`** - Tumblr OAuth 1.0a authentication
  - Request token and access token exchange
  - Blog discovery and primary blog selection
  - OAuth 1.0a flow with Tumblr API v2

- **`x_auth.py`** - X (Twitter) OAuth2 with PKCE authentication
  - OAuth 2.0 Authorization Code Flow with PKCE
  - Access and refresh token management
  - User profile and timeline access
  - Enhanced security with PKCE implementation

## Common Patterns

All authentication modules follow these patterns:
- Secure token storage (database or file-based)
- Comprehensive error handling and validation
- User information retrieval and caching
- Token refresh and validation functions
- Consistent function naming and return formats