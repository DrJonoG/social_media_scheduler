#!/usr/bin/env python3
"""
Social Media Scheduler Pro - Main Entry Point

This is the main entry point for the Social Media Scheduler application.
It initialises the environment, starts the background scheduler, and launches
the Streamlit dashboard interface.

Usage:
    python main.py
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        import requests
        import apscheduler
        from dotenv import load_dotenv
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n💡 Please install dependencies:")
        print("   pip install -r requirements.txt")
        return False


def load_environment():
    """Load environment variables and validate configuration."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not load .env file: {e}")
        print("   The application will use system environment variables")
        return True


def initialise_scheduler():
    """Initialise the background scheduler for post scheduling."""
    try:
        from app.scheduler.apscheduler import scheduler
        print("✅ Background scheduler initialised")
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not initialise scheduler: {e}")
        print("   Scheduled posting may not work properly")
        return True  # Continue anyway as immediate posting should still work


def validate_project_structure():
    """Validate that essential project directories exist."""
    required_dirs = [
        "app",
        "app/ui",
        "app/platforms",
        "app/config.py"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not (project_root / dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Missing required directories/files: {', '.join(missing_dirs)}")
        print("   Please ensure you're running from the project root directory")
        return False
    
    print("✅ Project structure validated")
    return True


def check_platform_setup():
    """Check which platforms are configured and provide setup guidance."""
    platforms_status = {}
    
    # Check for credential files or environment variables
    credential_files = {
        "Facebook": project_root / "app" / "secure" / "facebook_token.json",
        "Instagram": project_root / "app" / "secure" / "instagram_token.json", 
        "Pinterest": project_root / "app" / "secure" / "pinterest_token.json",
        "Tumblr": project_root / "data" / "credentials" / "tumblr_credentials.json",
        "X": project_root / "app" / "secure" / "x_token.json"
    }
    
    configured_platforms = []
    unconfigured_platforms = []
    
    for platform, cred_file in credential_files.items():
        if cred_file.exists():
            platforms_status[platform] = "✅ Configured"
            configured_platforms.append(platform)
        else:
            platforms_status[platform] = "🔴 Not configured"
            unconfigured_platforms.append(platform)
    
    print(f"\n📱 Platform Status:")
    for platform, status in platforms_status.items():
        print(f"   {platform}: {status}")
    
    if configured_platforms:
        print(f"\n🎯 Ready to post to: {', '.join(configured_platforms)}")
    
    if unconfigured_platforms:
        print(f"\n💡 To configure additional platforms, run:")
        for platform in unconfigured_platforms:
            script_name = f"{platform.lower()}_setup.py"
            print(f"   python scripts/{script_name}")
    
    return True


def launch_streamlit():
    """Launch the Streamlit dashboard."""
    dashboard_path = project_root / "app" / "ui" / "dashboard.py"
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard not found at: {dashboard_path}")
        return False
    
    print(f"\n🚀 Launching Social Media Scheduler Pro...")
    print(f"   Dashboard: {dashboard_path}")
    print(f"   URL: http://localhost:8501")
    print(f"\n💡 Use Ctrl+C to stop the application")
    
    try:
        # Launch Streamlit with proper configuration
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.headless", "true",
            "--server.port", "8501",
            "--server.address", "localhost"
        ]
        
        subprocess.run(cmd, cwd=str(project_root))
        return True
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Application stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to launch Streamlit: {e}")
        return False


def print_banner():
    """Print application banner."""
    print("=" * 60)
    print("📱 SOCIAL MEDIA SCHEDULER PRO")
    print("=" * 60)
    print("🎯 Multi-platform social media content management")
    print("🤖 AI-powered content enhancement")
    print("📅 Advanced post scheduling")
    print("🔐 Secure OAuth authentication")
    print("=" * 60)


def print_help():
    """Print setup guidance and help information."""
    print(f"\n📚 Quick Start Guide:")
    print(f"1. Configure platforms: Run setup scripts in scripts/ directory")
    print(f"2. Set up AI (optional): Add API keys to .env file")
    print(f"3. Create content: Use the dashboard to write and enhance posts")
    print(f"4. Schedule or post: Choose immediate or scheduled publishing")
    
    print(f"\n🔧 Setup Scripts Available:")
    setup_scripts = [
        "facebook_setup.py - Facebook pages and posting",
        "instagram_setup.py - Instagram business accounts", 
        "pinterest_setup.py - Pinterest boards and pins",
        "tumblr_setup.py - Tumblr blogs and post types",
        "x_setup.py - X (Twitter) posting and media"
    ]
    
    for script in setup_scripts:
        print(f"   python scripts/{script}")


def main():
    """Main application entry point."""
    print_banner()
    
    # Validation checks
    if not validate_project_structure():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not load_environment():
        sys.exit(1)
    
    if not initialise_scheduler():
        print("   Continuing without full scheduler support...")
    
    # Platform status check
    check_platform_setup()
    
    # Show help information
    print_help()
    
    # Launch the application
    print(f"\n" + "=" * 60)
    success = launch_streamlit()
    
    if not success:
        print(f"\n❌ Failed to start the application")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error during startup: {e}")
        print(f"   Please check your configuration and try again")
        sys.exit(1)
