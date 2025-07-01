from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
from dotenv import load_dotenv
import sys

# Load environment
load_dotenv()

# Configurable interval in seconds (default: 60 seconds = 1 minute)
SCHEDULER_INTERVAL = int(os.getenv("SCHEDULER_INTERVAL", 60))

# Initialize background scheduler
scheduler = BackgroundScheduler()

def check_and_post_due_items():
    """Check for scheduled posts and post them if due."""
    try:
        from app.db.database import get_due_posts, update_post_status
        from app.config import USE_DATABASE
        
        if not USE_DATABASE:
            return  # Skip if database not configured
        
        print(f"🔍 Checking for scheduled posts... ({datetime.now().strftime('%H:%M:%S')})")
        now = datetime.now()
        due_posts = get_due_posts(now)

        if not due_posts:
            print("   No scheduled posts due at this time")
            return

        print(f"   Found {len(due_posts)} scheduled post(s) to process")

        for post in due_posts:
            try:
                platform = post['platform'].lower()
                content = post['content']
                media_path = post.get('media_path')
                post_id = post['id']
                
                print(f"📤 Posting to {platform}: {content[:50]}...")
                
                                 # Post to the appropriate platform
                if platform == "facebook":
                    from app.platforms.facebook import post_with_media_to_page, load_facebook_credentials
                    fb_creds = load_facebook_credentials()
                    if fb_creds:
                        # Create a simple media file object if media exists
                        media_file = None
                        if media_path and os.path.exists(media_path):
                            # Create a simple file-like object for the platform function
                            class MediaFile:
                                def __init__(self, file_path):
                                    self.name = os.path.basename(file_path)
                                    self.path = file_path
                                def getvalue(self):
                                    with open(self.path, 'rb') as f:
                                        return f.read()
                            media_file = MediaFile(media_path)
                        
                        result = post_with_media_to_page(
                            message=content,
                            page_token=fb_creds['page_token'],
                            page_id=fb_creds['page_id'],
                            media_file=media_file
                        )
                        
                        if result.get('success'):
                            update_post_status(post_id, 'published')
                            print(f"   ✅ Facebook post {post_id} published successfully")
                        else:
                            update_post_status(post_id, 'failed')
                            print(f"   ❌ Facebook post {post_id} failed: {result.get('message', 'Unknown error')}")
                    else:
                        update_post_status(post_id, 'failed')
                        print(f"   ❌ Facebook credentials not found")
                
                elif platform == "instagram":
                    from app.platforms.instagram import post_to_instagram, load_instagram_credentials
                    ig_creds = load_instagram_credentials()
                    if ig_creds:
                        # Create a simple media file object if media exists
                        media_file = None
                        if media_path and os.path.exists(media_path):
                            # Create a simple file-like object for the platform function
                            class MediaFile:
                                def __init__(self, file_path):
                                    self.name = os.path.basename(file_path)
                                    self.path = file_path
                                def getvalue(self):
                                    with open(self.path, 'rb') as f:
                                        return f.read()
                            media_file = MediaFile(media_path)
                        
                        result = post_to_instagram(
                            message=content,
                            access_token=ig_creds['access_token'],
                            ig_user_id=ig_creds['ig_user_id'],
                            media_file=media_file
                        )
                        
                        if result.get('success'):
                            update_post_status(post_id, 'published')
                            print(f"   ✅ Instagram post {post_id} published successfully")
                        else:
                            update_post_status(post_id, 'failed')
                            print(f"   ❌ Instagram post {post_id} failed: {result.get('message', 'Unknown error')}")
                    else:
                        update_post_status(post_id, 'failed')
                        print(f"   ❌ Instagram credentials not found")
                
                elif platform == "pinterest":
                    from app.platforms.pinterest import post_to_pinterest, load_pinterest_credentials
                    pinterest_creds = load_pinterest_credentials()
                    if pinterest_creds:
                        # Create a simple media file object if media exists
                        media_file = None
                        if media_path and os.path.exists(media_path):
                            # Create a simple file-like object for the platform function
                            class MediaFile:
                                def __init__(self, file_path):
                                    self.name = os.path.basename(file_path)
                                    self.path = file_path
                                def getvalue(self):
                                    with open(self.path, 'rb') as f:
                                        return f.read()
                            media_file = MediaFile(media_path)
                        
                        result = post_to_pinterest(
                            message=content,
                            access_token=pinterest_creds['access_token'],
                            user_id=pinterest_creds['user_id'],
                            media_file=media_file
                        )
                        
                        if result.get('success'):
                            update_post_status(post_id, 'published')
                            print(f"   ✅ Pinterest post {post_id} published successfully")
                        else:
                            update_post_status(post_id, 'failed')
                            print(f"   ❌ Pinterest post {post_id} failed: {result.get('message', 'Unknown error')}")
                    else:
                        update_post_status(post_id, 'failed')
                        print(f"   ❌ Pinterest credentials not found")
                
                elif platform == "tumblr":
                    from app.platforms.tumblr import post_to_tumblr
                    # Load media file if exists
                    media_path_param = None
                    if media_path and os.path.exists(media_path):
                        media_path_param = media_path
                    
                    result = post_to_tumblr(
                        message=content,
                        media_path=media_path_param
                    )
                    
                    if result.get('success'):
                        update_post_status(post_id, 'published')
                        print(f"   ✅ Tumblr post {post_id} published successfully")
                    else:
                        update_post_status(post_id, 'failed')
                        print(f"   ❌ Tumblr post {post_id} failed: {result.get('message', 'Unknown error')}")
                
                elif platform == "x":
                    from app.platforms.x import post_to_x
                    # Load media file if exists
                    media_paths = []
                    if media_path and os.path.exists(media_path):
                        media_paths = [media_path]
                    
                    result = post_to_x(
                        text=content,
                        media_paths=media_paths
                    )
                    
                    if result.get('success'):
                        update_post_status(post_id, 'published')
                        print(f"   ✅ X post {post_id} published successfully")
                    else:
                        update_post_status(post_id, 'failed')
                        print(f"   ❌ X post {post_id} failed: {result.get('message', 'Unknown error')}")
                
                else:
                    update_post_status(post_id, 'failed')
                    print(f"   ❌ Platform {platform} not supported by scheduler")
                    
            except Exception as e:
                update_post_status(post['id'], 'failed')
                print(f"   ❌ Failed to post ID {post['id']}: {str(e)}")

    except Exception as e:
        print(f"❌ Scheduler error: {str(e)}")

# Start the scheduler and add the job
scheduler.add_job(check_and_post_due_items, 'interval', seconds=SCHEDULER_INTERVAL)
scheduler.start()

print(f"✅ Background scheduler started (checking every {SCHEDULER_INTERVAL} seconds)")