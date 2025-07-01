# Contributing to Social Media Scheduler

We love your input! We want to make contributing to Social Media Scheduler as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## 🚀 Quick Start for Contributors

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a new branch for your feature
4. **Make** your changes
5. **Test** your changes
6. **Submit** a Pull Request

## 📋 Development Process

We use GitHub to host code, track issues and feature requests, and accept pull requests.

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/social-media-scheduler.git
cd social-media-scheduler

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (when available)
pip install -r requirements-dev.txt

# Set up pre-commit hooks (optional)
pre-commit install
```

## 🐛 Bug Reports

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

Use the [GitHub issue template](https://github.com/yourusername/social-media-scheduler/issues/new) for bug reports.

## 💡 Feature Requests

We love feature requests! Please:

1. **Check existing issues** to avoid duplicates
2. **Describe the feature** clearly and concisely
3. **Explain why** this feature would be useful
4. **Provide examples** of how it would work
5. **Consider the scope** - would this be useful to most users?

## 🎯 Areas We Need Help With

- **New Platform Support**: TikTok, LinkedIn, YouTube, etc.
- **UI/UX Improvements**: Better dashboard design
- **Testing**: More comprehensive test coverage
- **Documentation**: Setup guides, API docs
- **Performance**: Optimising scheduling and posting
- **Mobile**: Responsive design improvements

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest tests/test_facebook.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names
- Test both success and failure cases
- Mock external API calls

## 📝 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Maximum line length: 88 characters (Black formatter standard)
- Use type hints where possible

### Code Formatting

We use automated code formatting:

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .
```

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add TikTok platform support
fix: resolve authentication token refresh issue
docs: update installation instructions
test: add unit tests for Pinterest API
refactor: improve error handling in scheduler
```

## 🏗️ Architecture Guidelines

### Adding New Platforms

When adding support for a new social media platform:

1. **Authentication** (`app/auth/platform_name_auth.py`)
   - Implement OAuth flow
   - Handle token refresh
   - Save/load credentials

2. **Platform API** (`app/platforms/platform_name.py`)
   - Create posting functions
   - Handle media uploads
   - Implement error handling

3. **Setup Script** (`scripts/platform_name_setup.py`)
   - Interactive authentication
   - Credential validation
   - User guidance

4. **UI Integration** (`app/ui/dashboard.py`)
   - Add platform to selection
   - Platform-specific validation
   - Status indicators

5. **Documentation** (`setup/platform_name-auth-setup.md`)
   - Step-by-step setup guide
   - API key requirements
   - Troubleshooting

### Code Structure

```
app/
├── auth/           # Authentication modules
├── platforms/      # Platform API wrappers
├── ui/            # User interface components
├── ai/            # AI service integrations
├── scheduler/     # Background scheduling
├── db/            # Database operations
└── config.py      # Configuration management
```

## 📖 Documentation

### Updating Documentation

- Update `README.md` for user-facing changes
- Update `STRUCTURE.md` for architectural changes
- Create setup guides for new platforms
- Document any breaking changes

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots where helpful
- Keep it up-to-date with code changes

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on what's best for the community
- Show empathy towards other community members
- Be collaborative
- When we disagree, try to understand why

### Getting Help

- **GitHub Discussions** for questions and ideas
- **GitHub Issues** for bugs and feature requests
- **Pull Request comments** for code review discussions

## 🎉 Recognition

Contributors will be:

- Added to the contributors list
- Credited in release notes
- Mentioned in the README if significant contribution

## 📞 Contact

- **Maintainer**: [Your Name](mailto:your.email@example.com)
- **Project Issues**: [GitHub Issues](https://github.com/yourusername/social-media-scheduler/issues)
- **Security Issues**: [Security Policy](SECURITY.md)

---

Thank you for contributing! 🙏 