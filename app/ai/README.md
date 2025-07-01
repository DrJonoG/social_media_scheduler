# AI Service APIs

This directory contains API wrappers for AI/LLM services used for content enhancement and generation.

## Current AI Providers

- **`anthropic.py`** - Anthropic Claude integration
  - Text improvement and enhancement
  - Content expansion and condensation
  - Title generation for posts

- **`openai.py`** - OpenAI GPT integration
  - Content generation and editing
  - Image generation via DALL-E
  - Advanced text processing

- **`gemini.py`** - Google Gemini integration
  - Multimodal content processing
  - Image generation capabilities
  - Text enhancement and analysis

## Core Features

All AI APIs provide:
- **Text Enhancement**: Improve, expand, or condense content
- **Title Generation**: Create engaging post titles
- **Error Handling**: Graceful fallbacks and error reporting
- **Token Management**: Cost estimation and usage tracking

## Adding New AI Providers

When adding a new AI service:

1. Create `{provider}.py` following the naming convention
2. Implement the standard interface:
   - `call_prompt(system_prompt, user_prompt, max_tokens)`
   - `count_tokens(system_prompt, user_prompt)`
   - `get_model()` and `set_model(model)`
3. Add API key configuration to `app/config.py`
4. Update `app/ui/ai_helpers.py` to support the new provider
5. Add provider option to the UI selection

## Configuration

AI services are configured via environment variables:
- `ANTHROPIC_API_KEY` - For Claude models
- `OPENAI_API_KEY` - For GPT and DALL-E models  
- `GEMINI_API_KEY` - For Gemini models

Set these in your `.env` file or environment. 