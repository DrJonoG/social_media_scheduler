# Configuration settings for the app


import os
from dotenv import load_dotenv

# Force load .env with override to ensure correct values
load_dotenv(override=True)

# Database configuration
# Read from environment, default to False for safer file-based storage
db_setting = os.getenv("USE_DATABASE", "false").lower().strip()
USE_DATABASE = db_setting in ["true", "1", "yes", "on"]

# Social Media API Keys
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")

# Pinterest API Configuration
PINTEREST_CLIENT_ID = os.getenv("PINTEREST_CLIENT_ID")
PINTEREST_CLIENT_SECRET = os.getenv("PINTEREST_CLIENT_SECRET")
PINTEREST_REDIRECT_URI = os.getenv("PINTEREST_REDIRECT_URI")
PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN")
PINTEREST_REFRESH_TOKEN = os.getenv("PINTEREST_REFRESH_TOKEN")

# Tumblr API Configuration
TUMBLR_CLIENT_ID = os.getenv("TUMBLR_CLIENT_ID")
TUMBLR_CLIENT_SECRET = os.getenv("TUMBLR_CLIENT_SECRET")
TUMBLR_REDIRECT_URI = os.getenv("TUMBLR_REDIRECT_URI")
TUMBLR_ACCESS_TOKEN = os.getenv("TUMBLR_ACCESS_TOKEN")
TUMBLR_ACCESS_TOKEN_SECRET = os.getenv("TUMBLR_ACCESS_TOKEN_SECRET")

# X (Twitter) API Configuration - Hybrid OAuth approach
# OAuth 2.0 with PKCE for tweet posting (v2 API)
X_CLIENT_ID = os.getenv("X_CLIENT_ID")
X_CLIENT_SECRET = os.getenv("X_CLIENT_SECRET")
X_REDIRECT_URI = os.getenv("X_REDIRECT_URI")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
X_REFRESH_TOKEN = os.getenv("X_REFRESH_TOKEN")
# OAuth 1.0a credentials for media upload (v1.1 API - still required)
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")

# LLM API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
