# UI Module Documentation

This module contains the user interface components for the Social Media Scheduler, built with Streamlit. The module is designed with a modular architecture for maintainability and reusability.

---

## Module Structure

### Core Components

**📄 `dashboard.py`** - Multi-platform posting interface
- Primary UI for creating and publishing to multiple social media platforms
- Platform selection with checkboxes for simultaneous posting
- Batch posting with per-platform success/failure tracking
- Smart validation for platform-specific requirements
- Clean, focused presentation layer for complex multi-platform operations

**🧠 `ai_helpers.py`** - AI processing business logic
- Handles text enhancement using AI APIs (Anthropic, OpenAI, Gemini)
- Provides clean interface for AI operations
- Manages API initialization and error handling
- Centralised AI processing functionality

**📝 `ai_prompts.py`** - AI prompt templates and configuration
- Contains specialized prompt templates for different AI actions
- Supports: improve, expand, condense, generate_title
- Optimised prompts for social media content
- Easy to extend and modify AI behaviors

**🎨 `page_management.py`** - Platform page management interface
- UI components for managing social media page settings
- Currently supports Facebook profile/cover photo management
- Modular design for easy platform extension
- Separate from main posting workflow

**⚡ `session_state.py`** - Session state management
- Centralised Streamlit session state handling
- Clean state initialization and updates
- Helper functions for UI state management
- Consistent state management across components

---

## Usage Guidelines

### Running the Dashboard
```bash
# From project root
streamlit run app/ui/dashboard.py

# Or via main entry point
python main.py
```

### Key Features

#### ✅ **Multi-Platform Post Creation & Publishing**
- **Platform Selection**: Choose any combination of Facebook, Instagram, Pinterest, Tumblr, X, TikTok, Threads
- **Batch Posting**: Publish to multiple platforms simultaneously
- **Smart Validation**: Platform-specific requirements (Instagram requires media)
- **Text Enhancement**: AI-powered improvements (improve, expand, condense)
- **Comprehensive Results**: Per-platform success/failure with detailed feedback
- **Schedule Toggle**: Switch between "Post Now" and "Schedule Later" for all selected platforms
- **Content Persistence**: Form content preserved during multi-platform operations
- **Media Upload**: Support for images and videos with platform compatibility

#### ✅ **Smart Multi-Platform UI Management**
- **Dynamic Button Text**: "Publish to 3 Platforms" based on selection count
- **Platform Status Indicators**: Real-time connection status for all platforms
- **Selection Indicators**: Visual markers (📤) for chosen platforms
- **Smart Warnings**: Platform-specific requirement alerts
- **Batch Results Display**: Comprehensive success/failure breakdown
- **Clear All**: One-click content clearing with proper state reset
- **Button States**: Intelligent disabling during operations
- **Real-time Feedback**: Per-platform success/error messages with post IDs

#### ✅ **Platform Management**
- **Profile Pictures**: Update Facebook page profile pictures
- **Cover Photos**: Update Facebook page cover photos (two-step process)
- **Page Selection**: Manage multiple pages from one interface

---

## Technical Implementation

### Session State Management
The application uses a sophisticated session state system:

```python
from .session_state import initialize_session_state, clear_content

# Initialize on app start
initialize_session_state()

# Clear form content
clear_content()
```

### AI Text Processing
AI functionality is abstracted into a clean interface:

```python
from .ai_helpers import process_text_with_ai, is_ai_available

# Check availability
if is_ai_available():
    # Process text
    result = process_text_with_ai(text, "improve")
```

### Modular Components
Each UI section is handled by dedicated functions:

```python
# Render different sections
render_quick_actions()
render_platform_selection()
render_content_section()
render_page_management_for_platform("Facebook")
```

---

## Configuration Requirements

### Environment Variables
```env
# Required for AI features
ANTHROPIC_API_KEY=your_key_here

# Required for Facebook posting
FACEBOOK_CLIENT_ID=your_facebook_app_id
FACEBOOK_CLIENT_SECRET=your_facebook_app_secret
FACEBOOK_REDIRECT_URI=your_redirect_uri

# Storage mode
USE_DATABASE=false  # Use file-based storage
```

### File Structure
```
app/ui/
├── dashboard.py          # Main application interface
├── ai_helpers.py         # AI processing logic
├── ai_prompts.py         # AI prompt templates
├── page_management.py    # Page management components
├── session_state.py      # Session state helpers
└── README.md            # This documentation
```

---

## Troubleshooting

### Common Issues

**❌ Import Errors**
- Ensure you're running from the project root directory
- Check that all dependencies are installed: `pip install -r requirements.txt`

**❌ Facebook API Errors**
- Verify credentials in `.env` file
- Run authentication setup: `python scripts/facebook_setup.py`
- Check that USE_DATABASE setting matches your setup

**❌ AI Processing Errors**
- Confirm ANTHROPIC_API_KEY is set correctly
- Check API key has sufficient credits/permissions
- Verify internet connection for API calls

**❌ Clear Button Not Working**
- This typically indicates a session state issue
- Refresh the page to reset state
- Check for JavaScript errors in browser console

### Debug Information
The sidebar provides real-time debug information:
- Current mode (Post Now / Schedule)
- Platform and AI provider selection
- Connection status for each platform
- AI model information
- Session state details

---

## Extending the UI

### Adding New Platforms
1. Add platform option to `render_platform_selection()`
2. Create posting logic in `handle_post_submission()`
3. Add page management in `page_management.py`

### Adding New AI Providers
1. Add provider option to AI provider selection
2. Create API wrapper in `app/api/`
3. Update `ai_helpers.py` to support new provider
4. Configure API keys in `.env`

### Adding New AI Actions
1. Add prompt template to `ai_prompts.py`
2. Add button to `render_content_section()`
3. Update `handle_text_enhancement()` logic

---

## Performance Considerations

- **Lazy Loading**: AI API only initialized when needed
- **State Optimization**: Minimal session state updates
- **Async Operations**: Non-blocking UI during API calls
- **Memory Management**: Efficient file handling for media uploads

---

**Created for The Story Chamber**  
*Streamlined, professional social media management*