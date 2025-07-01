# App Module

This directory contains the core application logic and components for the Social Media Scheduler.

## Module Structure

### Authentication (`auth/`)
Handles OAuth authentication flows for all supported social media platforms:
- Facebook/Instagram OAuth2 authentication
- Pinterest OAuth2 authentication  
- Tumblr OAuth 1.0a authentication
- X (Twitter) OAuth 2.0 with PKCE authentication

### Platforms (`platforms/`)
API wrappers for social media platform interactions:
- Multi-platform posting capabilities
- Platform-specific content formatting
- Media upload and attachment handling
- Error handling and status reporting

### AI Integration (`ai/`)
AI service integrations for content enhancement:
- Anthropic Claude integration
- OpenAI GPT and DALL-E integration
- Google Gemini integration
- Text improvement, expansion, and condensation

### User Interface (`ui/`)
Streamlit-based web interface components:
- Multi-platform posting dashboard
- AI-powered content editing tools
- Platform management interfaces
- Session state management

### Scheduling (`scheduler/`)
Background task management for scheduled posting:
- APScheduler integration
- Multi-platform scheduling logic
- Automated posting execution

### Database (`db/`)
Data persistence and query utilities:
- MySQL connector and query executor
- Database schema management
- Platform credential storage

### Media (`media/`)
Media file handling and validation (planned):
- Image and video processing
- Format validation and conversion
- Media optimisation for platforms

## Configuration

The `config.py` file centralises application settings:
- Database connection configuration
- API key management
- Feature toggles (AI, database usage)
- Platform-specific settings

## Usage

All components are designed to work together seamlessly. The main entry point (`main.py`) initialises the web interface, which coordinates between authentication, platforms, AI services, and scheduling components.