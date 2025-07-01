# Multi-Platform Social Media APIs

This directory contains API wrappers for social media platforms supported by the multi-platform scheduler system.

## Current Platforms

- **`facebook.py`** - Facebook Pages API integration
  - Multi-platform batch posting compatibility
  - Post publishing with media support
  - Page management (profile/cover photos)
  - OAuth2 authentication handling
  - Real-time success/failure reporting

- **`instagram.py`** - Instagram Business API integration
  - Multi-platform batch posting via Facebook Graph API
  - Content publishing for business accounts
  - Requires Facebook page with linked Instagram Business account
  - Media hosting via Facebook for Instagram URL requirements
  - Smart validation for Instagram-specific requirements
  - Business account management and verification

- **`pinterest.py`** - Pinterest API v5 integration
  - Multi-platform batch posting compatibility
  - Pin creation with media upload support
  - Board discovery and management
  - OAuth2 authentication with Pinterest API
  - Optimised for vertical images (2:3 ratio)
  - Real-time success/failure reporting

- **`tumblr.py`** - Tumblr API v2 integration
  - Multi-platform batch posting compatibility
  - Multi-post type support (text, photo, video, link)
  - Blog discovery and primary blog selection
  - OAuth 1.0a authentication handling
  - Media upload with temporary file management
  - Content formatting with title extraction and tag addition

- **`x.py`** - X (Twitter) API v2 integration
  - Multi-platform batch posting compatibility
  - Text and media posting (280 character limit)
  - OAuth 2.0 with PKCE for enhanced security
  - Media upload via v1.1 API with v2 posting
  - Support for images (up to 4) and videos (1 per tweet)
  - Automatic token refresh handling
  - Real-time success/failure reporting

## Adding New Platforms

When adding support for a new platform:

1. Create `{platform}.py` following the naming convention
2. Implement these core functions:
   - Authentication and token management
   - Post publishing (text and media) with multi-platform compatibility
   - Error handling and validation with detailed feedback
   - Integration with batch posting system
3. Add authentication logic to `app/auth/{platform}_auth.py`
4. Update the UI to support the new platform in the checkbox grid
5. Create setup script in `scripts/{platform}_setup.py`
6. Add platform to `session_state.py` default platforms list

## Common Patterns

All platform APIs should:
- Handle OAuth2 authentication flows
- Support both immediate and scheduled posting
- Support multi-platform batch posting with individual success/failure tracking
- Provide clear error messages and logging with platform-specific guidance
- Follow the project's British English conventions
- Include comprehensive docstrings
- Return standardised success/failure dictionaries for UI integration 