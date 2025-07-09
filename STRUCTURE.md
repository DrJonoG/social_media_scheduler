# Project Structure

```
app/                     # Core application logic and components
  auth/                  # OAuth authentication and token management
  platforms/             # Social media platform API wrappers (Facebook, Instagram, X, TikTok, etc.)
  ai/                    # AI/LLM service APIs (Anthropic, OpenAI, Gemini)
  scheduler/             # Logic for scheduling and executing timed post publishing
  ui/                    # Web interface components (built with Streamlit)
  media/                 # Tools for validating or previewing images and videos
  db/                    # Database connectors and query utilities (MySQL or SQLite)
  api/                   # API components and endpoints (planned)
  secure/                # Secure token and credential storage (git-ignored)
  config.py              # Centralised application configuration (uses .env)

data/                    # Persistent local storage (git-ignored)
  logs/                  # Log files for posting results, errors, and debug info
  credentials/           # Platform credential storage (git-ignored)
  media/                 # User-uploaded media files (git-ignored)
  temp_media/            # Temporary media processing (git-ignored)
  posts.db               # Optional SQLite fallback database (git-ignored)

scripts/                 # Setup and utility scripts
  facebook_setup.py      # Facebook OAuth2 authentication and page token setup
  instagram_setup.py     # Instagram OAuth2 authentication and account setup
  pinterest_setup.py     # Pinterest OAuth2 authentication and board setup
  tumblr_setup.py        # Tumblr OAuth 1.0a authentication and blog setup
  x_setup.py             # X (Twitter) OAuth 2.0 with PKCE authentication setup
  tiktok_setup.py        # TikTok OAuth 2.0 authentication and account setup

setup/                   # Setup and usage guides
  facebook-auth-setup.md # Step-by-step Facebook authentication guide
  instagram-auth-setup.md # Step-by-step Instagram setup guide
  pinterest-auth-setup.md # Step-by-step Pinterest authentication guide
  tumblr-auth-setup.md   # Step-by-step Tumblr OAuth 1.0a setup guide
  x-auth-setup.md        # Step-by-step X (Twitter) OAuth 2.0 setup guide
  tiktok-auth-setup.md   # Step-by-step TikTok OAuth 2.0 setup guide
  database-structure.md  # Database schema and setup information

# Root Files
main.py                  # Main entry point for running the web app and scheduler
requirements.txt         # Python package dependencies
.env_example             # Environment variables template for setup

# Documentation
README.md                # Project overview, setup instructions, and features
STRUCTURE.md             # This file — explains the file and folder organisation
CONTRIBUTING.md          # Contributor guidelines and development setup
LICENSE                  # MIT License for open source distribution

# Configuration
.gitignore               # Git ignore rules for sensitive files and directories
```

## Key Notes

- **Security**: Directories marked as "git-ignored" contain sensitive data and are excluded from version control
- **Setup**: Use `.env_example` as a template to create your `.env` file with API keys
- **Dependencies**: Install required packages with `pip install -r requirements.txt`
- **Authentication**: Run setup scripts in `scripts/` to configure platform access
- **Documentation**: See `setup/` directory for detailed platform-specific guides
