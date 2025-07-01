"""
Page Management Component for Social Media Scheduler

This module contains the UI components and logic for managing social media page settings,
specifically Facebook page profile pictures and cover photos.
"""

import streamlit as st
from app.platforms.facebook import (
    load_facebook_credentials, 
    update_page_profile_picture, 
    update_page_cover_photo
)


def render_facebook_page_management():
    """
    Render the Facebook page management interface.
    
    This includes profile picture and cover photo management functionality.
    """
    st.markdown("---")
    
    with st.expander("🎨 Page Management", expanded=False):
        st.subheader("Update Page Appearance")
        
        fb_creds = load_facebook_credentials()
        if fb_creds:
            st.info(f"🏢 Managing: **{fb_creds['page_name']}**")
            
            # Profile Picture Section
            _render_profile_picture_section(fb_creds)
            
            # Cover Photo Section
            _render_cover_photo_section(fb_creds)
            
            # Tips section
            _render_tips_section()
        
        else:
            _render_no_credentials_warning()


def _render_profile_picture_section(fb_creds: dict):
    """Render the profile picture management section."""
    st.markdown("#### 📸 Profile Picture")
    profile_pic = st.file_uploader(
        "Upload new profile picture", 
        type=["png", "jpg", "jpeg"],
        key="profile_pic",
        help="Recommended: Square image, minimum 180x180 pixels"
    )
    
    if profile_pic:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.image(profile_pic, caption="New Profile Picture Preview", width=150)
        with col2:
            if st.button("📸 Update Profile Picture", type="secondary"):
                with st.spinner("Updating profile picture..."):
                    result = update_page_profile_picture(
                        page_token=fb_creds['page_token'],
                        page_id=fb_creds['page_id'],
                        image_file=profile_pic
                    )
                    
                    if result['success']:
                        st.success(f"🎉 {result['message']}")
                    else:
                        st.error(f"❌ {result['message']}")


def _render_cover_photo_section(fb_creds: dict):
    """Render the cover photo management section."""
    st.markdown("#### 🖼️ Cover Photo")
    cover_photo = st.file_uploader(
        "Upload new cover photo", 
        type=["png", "jpg", "jpeg"],
        key="cover_photo",
        help="Recommended: 1640x859 pixels (landscape orientation)"
    )
    
    if cover_photo:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.image(cover_photo, caption="New Cover Photo Preview", width=400)
        with col2:
            if st.button("🖼️ Update Cover Photo", type="secondary"):
                with st.spinner("Updating cover photo..."):
                    result = update_page_cover_photo(
                        page_token=fb_creds['page_token'],
                        page_id=fb_creds['page_id'],
                        image_file=cover_photo
                    )
                    
                    if result['success']:
                        st.success(f"🎉 {result['message']}")
                        if result.get('photo_id'):
                            st.info(f"📍 Photo ID: {result['photo_id']}")
                    else:
                        st.error(f"❌ {result['message']}")


def _render_tips_section():
    """Render the tips and guidelines section."""
    st.markdown("---")
    st.caption("💡 **Tips:**")
    st.caption("• Profile pictures appear as circles on Facebook")
    st.caption("• Cover photos are displayed at the top of your page")
    st.caption("• Changes may take a few minutes to appear across Facebook")


def _render_no_credentials_warning():
    """Render warning when Facebook credentials are not available."""
    st.warning("⚠️ Facebook credentials not found. Please run the authentication setup first.")
    st.code("python scripts/facebook_setup.py", language="bash")


def render_page_management_for_platform(platform: str):
    """
    Render page management interface for the specified platform.
    
    Args:
        platform (str): The platform to render management for
    """
    if platform == "Facebook":
        render_facebook_page_management()
    elif platform in ["TikTok", "Instagram", "X"]:
        st.info(f"📋 Page management for {platform} will be available in future updates.")
    else:
        st.warning(f"⚠️ Page management not supported for {platform}") 