# supabase_client.py
from supabase import create_client                      #
import streamlit as st
from datetime import datetime
import re

# ================= SUPABASE CONFIGURATION =================
def get_supabase():
    """Get Supabase client - works locally and on Hugging Face"""
    try:
        # Try to get from Streamlit secrets (Hugging Face or local)
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_PUBLISHABLE_KEY"]
    except:
        # Fallback for local testing (hardcoded)
        url = "https://pobnwbzcntlfozqpbgmj.supabase.co"
        key = "sb_publishable_btEddg2V38fI_EOYcbNrKQ_Ur9_tlt8"
    
    return create_client(url, key)

# ================= USER FUNCTIONS =================
def login_user(username, password):
    """Login user"""
    supabase = get_supabase()
    try:
        result = supabase.table('users').select('*').eq('username', username).eq('password', password).execute()
        if result.data:
            return True, result.data[0]
        return False, "Invalid credentials"
    except Exception as e:
        return False, str(e)

def create_user(username, password, bio=""):
    """Create new user"""
    supabase = get_supabase()
    try:
        # Check if user exists
        existing = supabase.table('users').select('*').eq('username', username).execute()
        if existing.data:
            return False, "Username already exists"
        
        # Create user - simplified without image for now
        user_data = {
            'username': username,
            'password': password,
            'bio': bio,
            'following': [],
            'followers': []
        }
        
        result = supabase.table('users').insert(user_data).execute()
        return True, result.data[0] if result.data else None
    except Exception as e:
        return False, str(e)

def get_user(username):
    """Get user data"""
    supabase = get_supabase()
    try:
        result = supabase.table('users').select('*').eq('username', username).execute()
        return result.data[0] if result.data else None
    except:
        return None

def update_user(username, updates):
    """Update user profile"""
    supabase = get_supabase()
    try:
        result = supabase.table('users').update(updates).eq('username', username).execute()
        return True, result.data
    except Exception as e:
        return False, str(e)

def follow_user(current_user, target_user):
    """Follow a user"""
    supabase = get_supabase()
    try:
        # Get current user's following list
        current = get_user(current_user)
        following = current.get('following', [])
        if target_user not in following:
            following.append(target_user)
            supabase.table('users').update({'following': following}).eq('username', current_user).execute()
        
        # Get target user's followers list
        target = get_user(target_user)
        followers = target.get('followers', [])
        if current_user not in followers:
            followers.append(current_user)
            supabase.table('users').update({'followers': followers}).eq('username', target_user).execute()
            
            # Create notification
            add_notification(target_user, 'follow', f"{current_user} started following you", None)
        
        return True
    except Exception as e:
        print(f"Follow error: {e}")
        return False

def unfollow_user(current_user, target_user):
    """Unfollow a user"""
    supabase = get_supabase()
    try:
        # Remove from current user's following
        current = get_user(current_user)
        following = current.get('following', [])
        if target_user in following:
            following.remove(target_user)
            supabase.table('users').update({'following': following}).eq('username', current_user).execute()
        
        # Remove from target user's followers
        target = get_user(target_user)
        followers = target.get('followers', [])
        if current_user in followers:
            followers.remove(current_user)
            supabase.table('users').update({'followers': followers}).eq('username', target_user).execute()
        
        return True
    except Exception as e:
        return False

def get_all_users():
    """Get all users"""
    supabase = get_supabase()
    try:
        result = supabase.table('users').select('*').execute()
        return result.data if result.data else []
    except:
        return []

# ================= POST FUNCTIONS =================
def create_post(post_data):
    """Create new post"""
    supabase = get_supabase()
    try:
        # Ensure all required fields exist
        post_data.setdefault('liked_by', [])
        post_data.setdefault('comments', [])
        post_data.setdefault('shares', 0)
        post_data.setdefault('original_post', None)
        post_data.setdefault('created_at', datetime.now().isoformat())
        
        result = supabase.table('posts').insert(post_data).execute()
        return True, result.data
    except Exception as e:
        print(f"Create post error: {e}")
        return False, str(e)

def get_all_posts():
    """Get all posts for feed"""
    supabase = get_supabase()
    try:
        result = supabase.table('posts').select('*').order('created_at', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Get posts error: {e}")
        return []

def get_user_posts(username):
    """Get posts by user"""
    supabase = get_supabase()
    try:
        result = supabase.table('posts').select('*').eq('username', username).order('created_at', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        return []

def update_post(post_id, updates):
    """Update post (like, comments, etc.)"""
    supabase = get_supabase()
    try:
        result = supabase.table('posts').update(updates).eq('id', post_id).execute()
        return True
    except Exception as e:
        print(f"Update post error: {e}")
        return False

def delete_post(post_id):
    """Delete post"""
    supabase = get_supabase()
    try:
        supabase.table('posts').delete().eq('id', post_id).execute()
        return True
    except Exception as e:
        return False

# ================= SAVED POSTS FUNCTIONS =================
def save_post(username, post_id):
    """Save post for user"""
    supabase = get_supabase()
    try:
        existing = supabase.table('saved_posts').select('*').eq('username', username).eq('post_id', post_id).execute()
        if not existing.data:
            supabase.table('saved_posts').insert({
                'username': username,
                'post_id': post_id,
                'saved_at': datetime.now().isoformat()
            }).execute()
        return True
    except Exception as e:
        return False

def unsave_post(username, post_id):
    """Remove saved post"""
    supabase = get_supabase()
    try:
        supabase.table('saved_posts').delete().eq('username', username).eq('post_id', post_id).execute()
        return True
    except Exception as e:
        return False

def get_saved_posts(username):
    """Get user's saved posts"""
    supabase = get_supabase()
    try:
        saved = supabase.table('saved_posts').select('post_id').eq('username', username).execute()
        post_ids = [s['post_id'] for s in saved.data] if saved.data else []
        
        if not post_ids:
            return []
        
        posts = supabase.table('posts').select('*').in_('id', post_ids).execute()
        return posts.data if posts.data else []
    except Exception as e:
        return []

# ================= NOTIFICATION FUNCTIONS =================
def add_notification(username, notif_type, message, post_id=None):
    """Add notification"""
    supabase = get_supabase()
    try:
        supabase.table('notifications').insert({
            'username': username,
            'type': notif_type,
            'text': message,
            'post_id': post_id,
            'is_read': False,
            'created_at': datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        return False

def get_notifications(username):
    """Get user's notifications"""
    supabase = get_supabase()
    try:
        result = supabase.table('notifications').select('*').eq('username', username).order('created_at', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        return []

def clear_notifications(username):
    """Clear all notifications for user"""
    supabase = get_supabase()
    try:
        supabase.table('notifications').delete().eq('username', username).execute()
        return True
    except Exception as e:
        return False

# ================= HELPER FUNCTIONS =================
def time_ago(timestamp):
    """Convert timestamp to 'time ago' string"""
    if not timestamp:
        return "Recently"
    try:
        dt = datetime.fromisoformat(timestamp)
        diff = (datetime.now() - dt).total_seconds()
        if diff < 60:
            return "Just now"
        elif diff < 3600:
            return f"{int(diff // 60)} min ago"
        elif diff < 86400:
            return f"{int(diff // 3600)} hr ago"
        else:
            return f"{int(diff // 86400)} days ago"
    except:
        return "Recently"

def extract_hashtags(text):
    """Extract hashtags from text"""
    return re.findall(r'#(\w+)', text)

def get_trending_hashtags(posts, limit=5):
    """Get trending hashtags from posts"""
    hashtag_count = {}
    for post in posts:
        hashtags = extract_hashtags(post.get('text', ''))
        for tag in hashtags:
            hashtag_count[tag] = hashtag_count.get(tag, 0) + 1
    sorted_tags = sorted(hashtag_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_tags[:limit]
