import streamlit as st
from datetime import datetime, timedelta
import time
import sys
import os

# Add the project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.ui.session_state import (
    initialize_session_state, clear_content, set_posting_state,
    set_ai_processing_state, update_text_content, update_title_content,
    is_any_operation_in_progress, get_form_key_suffix, get_session_debug_info
)

try:
    from app.platforms.facebook import post_with_media_to_page, load_facebook_credentials
    from app.platforms.instagram import post_to_instagram, load_instagram_credentials
    from app.platforms.pinterest import post_to_pinterest, load_pinterest_credentials
    from app.platforms.tumblr import post_to_tumblr, load_tumblr_credentials
    from app.platforms.x import post_to_x, load_x_credentials
    from app.ui.ai_helpers import process_text_with_ai, is_ai_available, get_ai_model_info
    from app.ui.page_management import render_page_management_for_platform
except ImportError:
    # Fallback for missing modules
    def initialize_session_state():
        if 'selected_platforms' not in st.session_state:
            st.session_state.selected_platforms = ["Facebook"]
        if 'ai_provider' not in st.session_state:
            st.session_state.ai_provider = "Anthropic"
        if 'title' not in st.session_state:
            st.session_state.title = ""
        if 'text' not in st.session_state:
            st.session_state.text = ""
        if 'post_now' not in st.session_state:
            st.session_state.post_now = True
    
    def is_any_operation_in_progress():
        return False
    
    def get_form_key_suffix():
        return ""
    
    def get_session_debug_info():
        return {"status": "active", "platform": st.session_state.platform}

initialize_session_state()

# Set page configuration with professional styling
st.set_page_config(
    page_title="Social Media Scheduler Pro", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Force container width - this actually works */
    .block-container {
        max-width: 1400px !important;
        margin: 0 auto !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* Professional styling for containers with our custom marker */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.section-marker) {
        background: white !important;
        padding: 2rem !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
        margin-bottom: 1.5rem !important;
        border: 1px solid #e8e8e8 !important;
        transition: all 0.3s ease !important;
    }
    
    /* Hover effect for our marked containers */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.section-marker):hover {
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.12) !important;
        border-color: #d0d0d0 !important;
        transform: translateY(-1px) !important;
    }
    
    /* Sidebar container specific styling */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.sidebar-marker) {
        background: white !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
        margin-bottom: 1.5rem !important;
        border: 1px solid #e8e8e8 !important;
        transition: all 0.3s ease !important;
    }
    
    /* Hide the marker elements */
    .section-marker, .sidebar-marker {
        display: none;
    }
    
    .section-title {
        color: #2c3e50;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        margin-top: -0.5rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.8rem;
        position: relative;
    }
    
    /* Gradient accent line on section titles */
    .section-title::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 60px;
        height: 2px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 1px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.4);
    }
    
    /* Primary button styling */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
    }
    
    /* AI button styling */
    .ai-button {
        background: linear-gradient(135deg, #9b59b6, #8e44ad) !important;
        box-shadow: 0 2px 8px rgba(155, 89, 182, 0.3) !important;
    }
    
    /* Form styling */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 2px solid #e8e8e8;
    }
    
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e8e8e8;
        padding: 0.75rem;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e8e8e8;
        padding: 0.75rem;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online {
        background-color: #27ae60;
        box-shadow: 0 0 8px rgba(39, 174, 96, 0.5);
    }
    
    .status-offline {
        background-color: #e74c3c;
    }
    
    /* Card styling */
    .info-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-left: 4px solid #3498db;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Upload area styling */
    .upload-area {
        border: 2px dashed #3498db;
        border-radius: 12px;
        padding: 2rem;
        background: #f8f9ff;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #2980b9;
        background: #f0f7ff;
    }
</style>
""", unsafe_allow_html=True)



# Header Section
st.markdown("""
<div class="header-container">
    <div class="header-title">📱 Social Media Scheduler Pro</div>
    <div class="header-subtitle">Streamline your social media content creation and scheduling</div>
</div>
""", unsafe_allow_html=True)

# Main Layout
col_main, col_sidebar = st.columns([3, 1])

with col_main:
    # Settings Section
    with st.container(border=True):
        st.markdown('<div class="section-marker"></div><div class="section-title">⚙️ Configuration</div>', unsafe_allow_html=True)
        
        settings_col1, settings_col2 = st.columns(2)
        with settings_col1:
            st.markdown("**🎯 Target Platforms**")
            
            # Define all available platforms
            available_platforms = ["Facebook", "Instagram", "Pinterest", "X", "TikTok", "Threads", "Tumblr"]
            
            # Create checkboxes for each platform in a vertical layout
            for platform in available_platforms:
                is_selected = platform in st.session_state.selected_platforms
                
                # Determine if platform is implemented
                if platform in ["Facebook", "Instagram", "Pinterest", "Tumblr", "X"]:
                    status_icon = "✅"
                    disabled = False
                else:
                    status_icon = "🔄"
                    disabled = True
                
                checkbox_selected = st.checkbox(
                    f"{status_icon} {platform}",
                    value=is_selected,
                    key=f"platform_{platform}",
                    disabled=disabled,
                    help=f"{'Post to ' + platform if not disabled else platform + ' - Coming soon'}"
                )
                
                # Update selected platforms
                if checkbox_selected and platform not in st.session_state.selected_platforms:
                    st.session_state.selected_platforms.append(platform)
                elif not checkbox_selected and platform in st.session_state.selected_platforms:
                    st.session_state.selected_platforms.remove(platform)
            
            # Show platform-specific warnings
            if st.session_state.selected_platforms:
                if "Instagram" in st.session_state.selected_platforms:
                    st.caption("⚠️ Instagram requires media (image/video)")
                if "Pinterest" in st.session_state.selected_platforms:
                    st.caption("📌 Pinterest works best with images (vertical 2:3 ratio)")
                if "Tumblr" in st.session_state.selected_platforms:
                    st.caption("🎨 Tumblr supports text, photo, video, and link posts")
                if "X" in st.session_state.selected_platforms:
                    st.caption("🐦 X supports text and media (280 character limit)")
                if len(st.session_state.selected_platforms) > 1:
                    st.caption(f"📤 Will post to {len(st.session_state.selected_platforms)} platforms")
            else:
                st.warning("⚠️ Please select at least one platform")
                
        with settings_col2:
            st.session_state.ai_provider = st.selectbox(
                "🤖 AI Assistant", 
                ["Anthropic", "OpenAI", "Gemini"],
                index=["Anthropic", "OpenAI", "Gemini"].index(st.session_state.ai_provider),
                help="Choose your preferred AI provider for content enhancement"
            )

    # Title Section
    with st.container(border=True):
        st.markdown('<div class="section-marker"></div><div class="section-title">📝 Post Title</div>', unsafe_allow_html=True)
        
        # Use a callback to properly handle title changes
        def update_title_callback():
            st.session_state.title = st.session_state.title_input
        
        st.text_input(
            "Post Title", 
            value=st.session_state.title, 
            key="title_input",
            placeholder="Enter your post title here...",
            help="Create an engaging title for your post",
            on_change=update_title_callback
        )
        
        # AI Title Generation Buttons
        generate_col, regen_col = st.columns(2)
        with generate_col:
            generate = st.button("✨ Generate", use_container_width=True, help="Generate a new title")
        with regen_col:
            regenerate = st.button("🔄 Retry", use_container_width=True, help="Regenerate title")

        if generate or regenerate:
            if not st.session_state.text.strip():
                st.warning("⚠️ Please add some content first to generate a title")
            else:
                set_ai_processing_state(True)
                try:
                    with st.spinner("🎯 Generating engaging title..."):
                        new_title = process_text_with_ai(st.session_state.text, "generate_title")
                        if new_title and new_title != st.session_state.text:
                            update_title_content(new_title)
                            st.success("✅ Title generated successfully!")
                        else:
                            st.error("❌ Failed to generate title. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error generating title: {str(e)}")
                finally:
                    set_ai_processing_state(False)
                    st.rerun()

    # Content Section
    with st.container(border=True):
        st.markdown('<div class="section-marker"></div><div class="section-title">✍️ Post Content</div>', unsafe_allow_html=True)
        
        # Use a callback to properly handle text area changes
        def update_text_callback():
            st.session_state.text = st.session_state.text_area_input
        
        st.text_area(
            "Content", 
            value=st.session_state.text, 
            height=200, 
            key="text_area_input",
            placeholder="Write your post content here. Be creative and engaging!",
            help="Write compelling content that resonates with your audience",
            on_change=update_text_callback
        )

        # AI Enhancement Buttons
        st.markdown("**🤖 AI Content Enhancement**")
        ai_col1, ai_col2, ai_col3, ai_col4 = st.columns(4)
        disable_ai = is_any_operation_in_progress()
        
        with ai_col1:
            improve = st.button("✨ Improve", use_container_width=True, disabled=disable_ai, help="Enhance content quality")
        with ai_col2:
            expand = st.button("📈 Expand", use_container_width=True, disabled=disable_ai, help="Add more detail")
        with ai_col3:
            condense = st.button("📉 Condense", use_container_width=True, disabled=disable_ai, help="Make it concise")
        with ai_col4:
            hashtags = st.button("# Hashtags", use_container_width=True, disabled=disable_ai, help="Generate hashtags")

        if any([improve, expand, condense, hashtags]):
            if not st.session_state.text.strip():
                st.warning("⚠️ Please add some content first")
            else:
                set_ai_processing_state(True)
                try:
                    if hashtags:
                        # Generate AI hashtags
                        with st.spinner("🤖 AI is generating relevant hashtags..."):
                            generated_hashtags = process_text_with_ai(st.session_state.text, "generate_hashtags")
                            if generated_hashtags and generated_hashtags.strip():
                                # Add hashtags to the content
                                hashtag_text = f"\n\n{generated_hashtags}"
                                st.session_state.text += hashtag_text
                                st.success("✅ AI-generated hashtags added successfully!")
                            else:
                                # Fallback to predefined hashtags
                                st.session_state.text += "\n\n#SocialMedia #Content #Marketing #Engagement"
                                st.success("✅ Fallback hashtags added successfully!")
                    else:
                        # Determine which AI action to perform
                        if improve:
                            action = "improve"
                            spinner_text = "🤖 AI is improving your content..."
                        elif expand:
                            action = "expand"
                            spinner_text = "🤖 AI is expanding your content..."
                        elif condense:
                            action = "condense"
                            spinner_text = "🤖 AI is condensing your content..."
                        
                        with st.spinner(spinner_text):
                            enhanced_text = process_text_with_ai(st.session_state.text, action)
                            if enhanced_text and enhanced_text != st.session_state.text:
                                update_text_content(enhanced_text)
                                st.success(f"✅ Content {action}d successfully!")
                            else:
                                st.error("❌ Failed to enhance content. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error processing content: {str(e)}")
                finally:
                    set_ai_processing_state(False)
                    st.rerun()

    # Media Upload Section
    with st.container(border=True):
        st.markdown('<div class="section-marker"></div><div class="section-title">🎨 Media Upload</div>', unsafe_allow_html=True)
        
        media = st.file_uploader(
            "Upload Media", 
            type=["png", "jpg", "jpeg", "gif", "mp4", "mov", "mpeg4"],
            help="Upload images or videos to accompany your post"
        )
        
        if media:
            st.success(f"📎 {media.name} uploaded successfully!")

    # Scheduling Section
    with st.container(border=True):
        st.markdown('<div class="section-marker"></div><div class="section-title">⏰ Publishing Schedule</div>', unsafe_allow_html=True)
        
        st.session_state.post_now = st.toggle("🚀 Post Immediately", value=st.session_state.post_now)
        
        if not st.session_state.post_now:
            sched_col1, sched_col2 = st.columns(2)
            with sched_col1:
                date = st.date_input("📅 Publication Date", min_value=datetime.now().date())
            with sched_col2:
                time_input = st.time_input("🕐 Publication Time")
            
            schedule_time = datetime.combine(date, time_input)
            now = datetime.now()
            
            # Validate that the scheduled time is in the future
            if schedule_time <= now:
                st.error("⚠️ Scheduled time must be in the future!")
                if date == now.date():
                    st.caption(f"💡 Current time: {now.strftime('%I:%M %p')} - Please select a time after this.")
                schedule_time_valid = False
            else:
                schedule_time_valid = True
                
            # Calculate time until publication
            time_until = schedule_time - now
            hours_until = int(time_until.total_seconds() // 3600)
            minutes_until = int((time_until.total_seconds() % 3600) // 60)
            
            if schedule_time_valid:
                st.markdown(f"""
                <div class="info-card">
                    <strong>📋 Scheduled Publication:</strong><br>
                    {schedule_time.strftime('%A, %B %d, %Y at %I:%M %p')}<br>
                    <small>⏱️ Publishing in {hours_until}h {minutes_until}m</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="info-card" style="border-left: 4px solid #e74c3c; background: #fdf2f2;">
                    <strong>❌ Invalid Schedule Time:</strong><br>
                    {schedule_time.strftime('%A, %B %d, %Y at %I:%M %p')}<br>
                    <small>⚠️ This time has already passed</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            schedule_time = None
            schedule_time_valid = True
    
    # Store schedule_time and validity in session state for use in submit handler
    if 'schedule_time' not in st.session_state or schedule_time != st.session_state.get('schedule_time'):
        st.session_state.schedule_time = schedule_time
    
    # Store schedule time validity 
    if not st.session_state.post_now:
        st.session_state.schedule_time_valid = schedule_time_valid
    else:
        st.session_state.schedule_time_valid = True

    # Submit Section
    st.markdown("---")
    submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
    with submit_col2:
        # Dynamic button text based on selections
        if not st.session_state.selected_platforms:
            button_text = "⚠️ Select Platform(s) First"
            button_disabled = True
        elif not st.session_state.get('schedule_time_valid', True):
            button_text = "⚠️ Fix Schedule Time First"
            button_disabled = True
        else:
            platform_count = len(st.session_state.selected_platforms)
            if st.session_state.post_now:
                button_text = f"🚀 Publish to {platform_count} Platform{'s' if platform_count > 1 else ''}"
            else:
                button_text = f"📅 Schedule for {platform_count} Platform{'s' if platform_count > 1 else ''}"
            button_disabled = False
        
        submit = st.button(button_text, type="primary", use_container_width=True, disabled=button_disabled)

    if submit:
        # Validate content
        if not st.session_state.text.strip() and not st.session_state.title.strip():
            st.error("⚠️ Please add some content before posting!")
        elif not st.session_state.selected_platforms:
            st.error("⚠️ Please select at least one platform!")
        elif not st.session_state.post_now and not st.session_state.get('schedule_time_valid', True):
            st.error("⚠️ Please select a valid future date and time for scheduling!")
        elif not st.session_state.post_now and st.session_state.schedule_time and st.session_state.schedule_time <= datetime.now():
            st.error("⚠️ Scheduled time must be in the future. Please adjust your selection.")
        else:
            # Pre-validate platform-specific requirements
            validation_errors = []
            if "Instagram" in st.session_state.selected_platforms and not media:
                validation_errors.append("Instagram requires media (image or video)")
            
            if validation_errors:
                for error in validation_errors:
                    st.error(f"❌ {error}")
            else:
                set_posting_state(True)
                try:
                    if st.session_state.post_now:
                        # Post immediately to all selected platforms
                        full_content = f"{st.session_state.title}\n\n{st.session_state.text}" if st.session_state.title else st.session_state.text
                        
                        posting_results = {}
                        
                        with st.spinner("📤 Publishing to selected platforms..."):
                            for platform in st.session_state.selected_platforms:
                                try:
                                    if platform == "Facebook":
                                        fb_creds = load_facebook_credentials()
                                        if fb_creds:
                                            result = post_with_media_to_page(
                                                message=full_content,
                                                page_token=fb_creds['page_token'],
                                                page_id=fb_creds['page_id'],
                                                media_file=media
                                            )
                                            posting_results[platform] = result
                                        else:
                                            posting_results[platform] = {
                                                "success": False,
                                                "message": "Credentials not found. Run facebook_setup.py"
                                            }
                                    
                                    elif platform == "Instagram":
                                        ig_creds = load_instagram_credentials()
                                        if ig_creds:
                                            result = post_to_instagram(
                                                message=full_content,
                                                access_token=ig_creds['access_token'],
                                                ig_user_id=ig_creds['ig_user_id'],
                                                media_file=media
                                            )
                                            posting_results[platform] = result
                                        else:
                                            posting_results[platform] = {
                                                "success": False,
                                                "message": "Credentials not found. Run instagram_setup.py"
                                            }
                                    
                                    elif platform == "Pinterest":
                                        pinterest_creds = load_pinterest_credentials()
                                        if pinterest_creds:
                                            result = post_to_pinterest(
                                                message=full_content,
                                                access_token=pinterest_creds['access_token'],
                                                user_id=pinterest_creds['user_id'],
                                                media_file=media
                                            )
                                            posting_results[platform] = result
                                        else:
                                            posting_results[platform] = {
                                                "success": False,
                                                "message": "Credentials not found. Run pinterest_setup.py"
                                            }
                                    
                                    elif platform == "Tumblr":
                                        tumblr_creds = load_tumblr_credentials()
                                        if tumblr_creds:
                                            # Save media file temporarily if uploaded
                                            media_path = None
                                            if media:
                                                import tempfile
                                                import os
                                                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{media.name.split('.')[-1]}") as tmp_file:
                                                    tmp_file.write(media.getvalue())
                                                    media_path = tmp_file.name
                                            
                                            result = post_to_tumblr(
                                                message=full_content,
                                                media_path=media_path
                                            )
                                            posting_results[platform] = result
                                            
                                            # Clean up temporary file
                                            if media_path and os.path.exists(media_path):
                                                try:
                                                    os.unlink(media_path)
                                                except:
                                                    pass
                                        else:
                                            posting_results[platform] = {
                                                "success": False,
                                                "message": "Credentials not found. Run tumblr_setup.py"
                                            }
                                    
                                    elif platform == "X":
                                        x_creds = load_x_credentials()
                                        if x_creds:
                                            # Save media file temporarily if uploaded
                                            media_paths = []
                                            if media:
                                                import tempfile
                                                import os
                                                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{media.name.split('.')[-1]}") as tmp_file:
                                                    tmp_file.write(media.getvalue())
                                                    media_paths = [tmp_file.name]
                                            
                                            result = post_to_x(
                                                text=full_content,
                                                media_paths=media_paths
                                            )
                                            posting_results[platform] = result
                                            
                                            # Clean up temporary files
                                            for media_path in media_paths:
                                                if os.path.exists(media_path):
                                                    try:
                                                        os.unlink(media_path)
                                                    except:
                                                        pass
                                        else:
                                            posting_results[platform] = {
                                                "success": False,
                                                "message": "Credentials not found. Run x_setup.py"
                                            }
                                    
                                    else:
                                        posting_results[platform] = {
                                            "success": False,
                                            "message": f"{platform} posting not yet implemented"
                                        }
                                        
                                except Exception as e:
                                    posting_results[platform] = {
                                        "success": False,
                                        "message": f"Error posting to {platform}: {str(e)}"
                                    }
                        
                        # Display results
                        successful_posts = [p for p, r in posting_results.items() if r.get('success')]
                        failed_posts = [p for p, r in posting_results.items() if not r.get('success')]
                        
                        if successful_posts:
                            st.success(f"🎉 Successfully posted to: {', '.join(successful_posts)}")
                            st.balloons()
                            
                            # Show post IDs
                            for platform in successful_posts:
                                result = posting_results[platform]
                                if result.get('post_id'):
                                    st.info(f"📍 {platform} Post ID: {result['post_id']}")
                        
                        if failed_posts:
                            st.error(f"❌ Failed to post to: {', '.join(failed_posts)}")
                            for platform in failed_posts:
                                result = posting_results[platform]
                                st.error(f"🔸 {platform}: {result.get('message', 'Unknown error')}")
                    
                    else:
                        # Schedule for later
                        with st.spinner("📅 Scheduling posts for selected platforms..."):
                            try:
                                from app.db.database import insert_post
                                from app.config import USE_DATABASE
                                
                                full_content = f"{st.session_state.title}\n\n{st.session_state.text}" if st.session_state.title else st.session_state.text
                                
                                if USE_DATABASE:
                                    # Save media file if uploaded
                                    media_path = None
                                    if media:
                                        import os
                                        media_dir = "data/media"
                                        os.makedirs(media_dir, exist_ok=True)
                                        media_path = f"{media_dir}/{media.name}"
                                        with open(media_path, "wb") as f:
                                            f.write(media.getvalue())
                                    
                                    # Insert scheduled post for each platform
                                    scheduled_count = 0
                                    for platform in st.session_state.selected_platforms:
                                        try:
                                            insert_post(
                                                platform=platform.lower(),
                                                content=full_content,
                                                media_path=media_path,
                                                scheduled_time=st.session_state.schedule_time,
                                                status="scheduled"
                                            )
                                            scheduled_count += 1
                                        except Exception as e:
                                            st.error(f"❌ Failed to schedule {platform}: {str(e)}")
                                    
                                    if scheduled_count > 0:
                                        st.success(f"📅 Scheduled {scheduled_count} post(s) successfully!")
                                        st.info(f"📋 Scheduled for: {st.session_state.schedule_time.strftime('%A, %B %d, %Y at %I:%M %p')}")
                                        st.info(f"📤 Platforms: {', '.join(st.session_state.selected_platforms)}")
                                else:
                                    st.error("❌ Database not configured. Cannot schedule posts without database.")
                            except Exception as e:
                                st.error(f"❌ Failed to schedule posts: {str(e)}")
                                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                finally:
                    set_posting_state(False)

# Sidebar
with col_sidebar:
    with st.container(border=True):
        st.markdown('<div class="sidebar-marker"></div><div class="section-title">📊 Status Dashboard</div>', unsafe_allow_html=True)
        
        # Connection Status
        st.markdown("**🔗 Platform Connections**")
        
        # Show all platforms and their status
        all_platforms = ["Facebook", "Instagram", "Pinterest", "X", "TikTok", "Threads", "Tumblr"]
        
        for platform in all_platforms:
            try:
                is_selected = platform in st.session_state.selected_platforms
                selection_indicator = "📤 " if is_selected else "   "
                
                if platform == "Facebook":
                    fb_creds = load_facebook_credentials()
                    platform_status = "🟢" if fb_creds else "🔴"
                    status_text = "Connected" if fb_creds else "Not configured"
                    
                    st.write(f"{selection_indicator}{platform_status} {platform}: {status_text}")
                    if fb_creds:
                        st.caption(f"     Page: {fb_creds['page_name']}")
                    elif is_selected:
                        st.caption("     ⚠️ Run facebook_setup.py")
                
                elif platform == "Instagram":
                    ig_creds = load_instagram_credentials()
                    platform_status = "🟢" if ig_creds else "🔴"
                    status_text = "Connected" if ig_creds else "Not configured"
                    
                    st.write(f"{selection_indicator}{platform_status} {platform}: {status_text}")
                    if ig_creds:
                        st.caption(f"     Account: @{ig_creds['username']}")
                    elif is_selected:
                        st.caption("     ⚠️ Run instagram_setup.py")
                
                elif platform == "Pinterest":
                    pinterest_creds = load_pinterest_credentials()
                    platform_status = "🟢" if pinterest_creds else "🔴"
                    status_text = "Connected" if pinterest_creds else "Not configured"
                    
                    st.write(f"{selection_indicator}{platform_status} {platform}: {status_text}")
                    if pinterest_creds:
                        st.caption(f"     Account: @{pinterest_creds['username']}")
                        boards_count = len(pinterest_creds.get('boards', []))
                        if boards_count > 0:
                            st.caption(f"     Boards: {boards_count} available")
                    elif is_selected:
                        st.caption("     ⚠️ Run pinterest_setup.py")
                
                elif platform == "Tumblr":
                    tumblr_creds = load_tumblr_credentials()
                    platform_status = "🟢" if tumblr_creds else "🔴"
                    status_text = "Connected" if tumblr_creds else "Not configured"
                    
                    st.write(f"{selection_indicator}{platform_status} {platform}: {status_text}")
                    if tumblr_creds:
                        st.caption(f"     Account: @{tumblr_creds.get('username', 'Unknown')}")
                        if tumblr_creds.get('blog_title'):
                            st.caption(f"     Blog: {tumblr_creds['blog_title']}")
                    elif is_selected:
                        st.caption("     ⚠️ Run tumblr_setup.py")
                
                elif platform == "X":
                    x_creds = load_x_credentials()
                    platform_status = "🟢" if x_creds else "🔴"
                    status_text = "Connected" if x_creds else "Not configured"
                    
                    st.write(f"{selection_indicator}{platform_status} {platform}: {status_text}")
                    if x_creds:
                        st.caption(f"     Account: @{x_creds.get('username', 'Unknown')}")
                        if x_creds.get('name'):
                            st.caption(f"     Name: {x_creds['name']}")
                    elif is_selected:
                        st.caption("     ⚠️ Run x_setup.py")
                
                else:
                    platform_status = "🔄"
                    status_text = "Coming soon"
                    st.write(f"{selection_indicator}{platform_status} {platform}: {status_text}")
                    if is_selected:
                        st.caption("     ⚠️ Not yet implemented")
                        
            except Exception as e:
                st.write(f"{selection_indicator}🔴 {platform}: Error")
                if is_selected:
                    st.caption(f"     Error: {str(e)}")
        
        # Show selected platforms summary
        if st.session_state.selected_platforms:
            st.markdown("---")
            st.markdown(f"**📤 Selected for Posting:** {', '.join(st.session_state.selected_platforms)}")
        
        # AI Status  
        st.markdown("**🤖 AI Assistant**")
        try:
            ai_available = is_ai_available()
            model_info = get_ai_model_info()
            ai_status = "🟢 Ready" if ai_available else "🔴 Not configured"
            st.write(f"{st.session_state.ai_provider}: {ai_status}")
            if ai_available:
                st.caption(f"Model: {model_info.get('model', 'Unknown')}")
            else:
                st.caption("Check API key configuration")
        except Exception:
            ai_status = "🔴 Error"
            st.write(f"{st.session_state.ai_provider}: {ai_status}")
        
        # Content Stats
        st.markdown("**📈 Content Analytics**")
        if st.session_state.title:
            st.metric("Title Length", f"{len(st.session_state.title)} chars")
        if st.session_state.text:
            st.metric("Content Length", f"{len(st.session_state.text)} chars")
            word_count = len(st.session_state.text.split())
            st.metric("Word Count", f"{word_count} words")
        
        # Quick Actions
        st.markdown("**⚡ Quick Actions**")
        if st.button("🗑️ Clear All", use_container_width=True):
            clear_content()
            st.success("✅ Content cleared!")
            st.rerun()
        
        if st.button("💾 Save Draft", use_container_width=True):
            if st.session_state.text.strip() or st.session_state.title.strip():
                try:
                    from app.config import USE_DATABASE
                    import json
                    import os
                    from datetime import datetime
                    
                    draft_data = {
                        "title": st.session_state.title,
                        "content": st.session_state.text,
                        "selected_platforms": st.session_state.selected_platforms,
                        "ai_provider": st.session_state.ai_provider,
                        "saved_at": datetime.now().isoformat()
                    }
                    
                    if USE_DATABASE:
                        # Save to database (could create a drafts table)
                        from app.db.database import insert_post
                        # Save draft for each selected platform
                        for platform in st.session_state.selected_platforms:
                            insert_post(
                                platform=platform.lower(),
                                content=f"{st.session_state.title}\n\n{st.session_state.text}" if st.session_state.title else st.session_state.text,
                                media_path=None,
                                scheduled_time=datetime.now() + timedelta(hours=24),  # Dummy future time
                                status="draft"
                            )
                        st.success("💾 Draft saved to database!")
                    else:
                        # Save to file
                        drafts_dir = "data/drafts"
                        os.makedirs(drafts_dir, exist_ok=True)
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        draft_file = f"{drafts_dir}/draft_{timestamp}.json"
                        
                        with open(draft_file, 'w') as f:
                            json.dump(draft_data, f, indent=2)
                        
                        st.success(f"💾 Draft saved to {draft_file}")
                        
                except Exception as e:
                    st.error(f"❌ Failed to save draft: {str(e)}")
            else:
                st.warning("⚠️ No content to save!")
        
        # Help Section
        with st.expander("❓ Need Help?"):
            st.markdown("""
            **Getting Started:**
            1. Select your platform and AI provider
            2. Create an engaging title
            3. Write your content
            4. Use AI to enhance your post
            5. Upload media (optional)
            6. Choose to post now or schedule
            7. Hit publish!
            
            **Tips:**
            - Use emojis to make posts engaging
            - Keep titles under 60 characters
            - Include relevant hashtags
            - Preview before publishing
            """)