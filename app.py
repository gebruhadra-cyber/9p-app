import streamlit as st
import uuid
import base64
from datetime import datetime
import os
import tempfile
import traceback

# ================= DEBUG INFO (remove later) =================
st.write("### Debug Info")
st.write(f"Python version: {__import__('sys').version}")

# Test Supabase connection
try:
    from supabase import create_client
    
    # Try to get secrets
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_PUBLISHABLE_KEY"]
        st.success("✅ Secrets found!")
        st.write(f"URL: {url[:30]}...")
    except Exception as e:
        st.error(f"❌ Secrets error: {e}")
        st.stop()
    
    # Test connection
    try:
        supabase = create_client(url, key)
        result = supabase.table('users').select('count').execute()
        st.success("✅ Supabase connected!")
        st.write(f"Users count: {result.data}")
    except Exception as e:
        st.error(f"❌ Connection error: {e}")
        st.stop()
        
except Exception as e:
    st.error(f"❌ Import error: {e}")
    st.stop()

st.write("---")
# ================= END DEBUG =================

# Rest of your app code...
# Import from supabase_client
from supabase_client import (
    get_supabase, login_user, create_user, get_user, get_all_users,
    get_all_posts, create_post, update_post, delete_post,
    follow_user, unfollow_user, save_post, unsave_post, get_saved_posts,
    add_notification, get_notifications, clear_notifications,
    time_ago, extract_hashtags, get_trending_hashtags
)

# ================= PAGE CONFIGURATION =================
st.set_page_config(
    page_title="9P Social",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="auto"
)

# ================= SESSION STATE INITIALIZATION =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'edit_post_id' not in st.session_state:
    st.session_state.edit_post_id = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ''
if 'selected_hashtag' not in st.session_state:
    st.session_state.selected_hashtag = None
if 'show_comments_for' not in st.session_state:
    st.session_state.show_comments_for = {}

# Load data from Supabase
supabase = get_supabase()
st.session_state.users = get_all_users()
st.session_state.posts = get_all_posts()
st.session_state.saved_posts = get_saved_posts(st.session_state.current_user) if st.session_state.current_user else []

# ================= CUSTOM CSS =================
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    .post-card {
        background: #1A1F2B;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 1px solid #2d2d2d;
        transition: all 0.3s ease;
    }
    .comment-box {
        background: #262D3D;
        padding: 10px;
        border-radius: 10px;
        margin: 8px 0;
    }
    .notification-unread {
        background: #2a3a4a;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #1877f2;
    }
    .notification-read {
        background: #1A1F2B;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #555;
    }
    .hashtag {
        color: #1877f2;
        cursor: pointer;
        text-decoration: none;
    }
    .hashtag:hover {
        text-decoration: underline;
    }
    div.stButton > button {
        background-color: #1877f2;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 14px;
        width: 100%;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #0d5fb9;
        transform: scale(0.98);
    }
    input, textarea {
        font-size: 16px !important;
        border-radius: 8px !important;
    }
    @media (max-width: 768px) {
        .post-card { padding: 10px; margin-bottom: 12px; }
        button { min-height: 44px; }
    }
    @media (min-width: 1025px) {
        .post-card { max-width: 800px; margin-left: auto; margin-right: auto; }
        .block-container { max-width: 900px; margin: 0 auto; }
    }
</style>
""", unsafe_allow_html=True)

# ================= LOGIN PAGE =================
def show_login():
    st.title("📱 9P Social")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)
                
                if submitted:
                    success, user = login_user(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.current_user = username
                        st.session_state.users = get_all_users()
                        st.session_state.posts = get_all_posts()
                        st.rerun()
                    else:
                        st.error(user)
        
        with tab2:
            with st.form("register_form"):
                new_user = st.text_input("Username")
                new_pass = st.text_input("Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                bio = st.text_area("Bio")
                submitted = st.form_submit_button("Register", use_container_width=True)
                
                if submitted:
                    if new_pass != confirm_pass:
                        st.error("Passwords don't match")
                    else:
                        success, result = create_user(new_user, new_pass, bio)
                        if success:
                            st.success("Account created! Please login.")
                            st.rerun()
                        else:
                            st.error(result)

# ================= HOME PAGE =================
def show_home():
    st.markdown("## 🏠 Feed")
    
    # Refresh posts
    st.session_state.posts = get_all_posts()
    posts = st.session_state.posts
    
    # Show trending hashtags
    trending = get_trending_hashtags(posts)
    if trending:
        st.markdown("### 🔥 Trending Hashtags")
        cols = st.columns(min(len(trending), 5))
        for idx, (tag, count) in enumerate(trending[:5]):
            with cols[idx % 5]:
                if st.button(f"#{tag} ({count})", key=f"trend_{tag}"):
                    st.session_state.selected_hashtag = tag
                    st.session_state.page = "trending"
                    st.rerun()
        st.markdown("---")
    
    if not posts:
        st.info("✨ No posts yet. Create the first post!")
        return
    
    for idx, post in enumerate(posts):
        post_id = post.get('id', f'post_{idx}')
        is_repost = post.get('original_post') is not None
        
        with st.container():
            st.markdown(f'<div class="post-card">', unsafe_allow_html=True)
            
            if is_repost:
                st.caption("🔄 Reposted")
            
            # Post header
            col1, col2, col3 = st.columns([1, 3, 2])
            with col1:
                st.write("👤")
            with col2:
                st.markdown(f"**{post.get('username', 'Unknown')}**")
                if post.get('created_at'):
                    st.caption(f"🕒 {time_ago(post['created_at'])}")
            with col3:
                if post.get('username') == st.session_state.current_user:
                    if st.button("✏️", key=f"edit_{post_id}"):
                        st.session_state.edit_post_id = post_id
                        st.rerun()
                    if st.button("🗑️", key=f"delete_{post_id}"):
                        delete_post(post_id)
                        st.session_state.posts = get_all_posts()
                        st.rerun()
            
            # Edit mode
            if st.session_state.edit_post_id == post_id:
                new_text = st.text_area("Edit post", value=post.get('text', ''), key=f"edit_text_{post_id}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save", key=f"save_edit_{post_id}"):
                        update_post(post_id, {'text': new_text})
                        st.session_state.edit_post_id = None
                        st.session_state.posts = get_all_posts()
                        st.rerun()
                with col2:
                    if st.button("Cancel", key=f"cancel_edit_{post_id}"):
                        st.session_state.edit_post_id = None
                        st.rerun()
                st.markdown("---")
            
            # Post text with clickable hashtags
            text = post.get('text', '')
            hashtags = extract_hashtags(text)
            for tag in hashtags:
                text = text.replace(f'#{tag}', f'<a href="#" class="hashtag">#{tag}</a>')
            st.markdown(text, unsafe_allow_html=True)
            
            # Post media
            if post.get('media_type') == "🎥 Video" and post.get('video'):
                try:
                    vid_data = post['video']
                    if isinstance(vid_data, str):
                        vid_bytes = base64.b64decode(vid_data)
                    else:
                        vid_bytes = vid_data
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmpfile:
                        tmpfile.write(vid_bytes)
                        st.video(tmpfile.name)
                    os.unlink(tmpfile.name)
                except:
                    st.warning("Could not load video")
            elif post.get('image'):
                try:
                    img_data = post['image']
                    if isinstance(img_data, str):
                        img_bytes = base64.b64decode(img_data)
                    else:
                        img_bytes = img_data
                    st.image(img_bytes, use_container_width=True)
                except:
                    pass
            
            # Action buttons
            liked = st.session_state.current_user in post.get('liked_by', [])
            like_count = len(post.get('liked_by', []))
            comment_count = len(post.get('comments', []))
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button(f"{'❤️' if liked else '🤍'} {like_count}", key=f"like_{post_id}"):
                    liked_by = post.get('liked_by', [])
                    if liked:
                        liked_by.remove(st.session_state.current_user)
                    else:
                        liked_by.append(st.session_state.current_user)
                        if st.session_state.current_user != post.get('username'):
                            add_notification(post.get('username'), 'like', f"{st.session_state.current_user} liked your post", post_id)
                    update_post(post_id, {'liked_by': liked_by})
                    st.session_state.posts = get_all_posts()
                    st.rerun()
            
            with col2:
                if st.button(f"💬 {comment_count}", key=f"comment_btn_{post_id}"):
                    st.session_state.show_comments_for[post_id] = not st.session_state.show_comments_for.get(post_id, False)
                    st.rerun()
            
            with col3:
                if st.button(f"🔄 {post.get('shares', 0)}", key=f"share_{post_id}"):
                    repost = {
                        'id': str(uuid.uuid4()),
                        'username': st.session_state.current_user,
                        'text': f"🔄 Reposted from {post.get('username')}: {post.get('text', '')[:100]}...",
                        'image': post.get('image'),
                        'video': post.get('video'),
                        'media_type': post.get('media_type', '📝 Text only'),
                        'liked_by': [],
                        'comments': [],
                        'shares': 0,
                        'original_post': post_id,
                        'created_at': datetime.now().isoformat()
                    }
                    create_post(repost)
                    update_post(post_id, {'shares': post.get('shares', 0) + 1})
                    add_notification(post.get('username'), 'share', f"{st.session_state.current_user} reposted your post", post_id)
                    st.session_state.posts = get_all_posts()
                    st.success("Reposted!")
                    st.rerun()
            
            with col4:
                saved = any(s.get('post_id') == post_id for s in st.session_state.saved_posts)
                if st.button(f"{'💾' if saved else '📁'} Save", key=f"save_{post_id}"):
                    if saved:
                        unsave_post(st.session_state.current_user, post_id)
                    else:
                        save_post(st.session_state.current_user, post_id)
                    st.session_state.saved_posts = get_saved_posts(st.session_state.current_user)
                    st.rerun()
            
            # Comments section
            if st.session_state.show_comments_for.get(post_id, False):
                st.markdown("---")
                st.markdown("### 💬 Comments")
                
                comments = post.get('comments', [])
                for comment_idx, comment in enumerate(comments):
                    st.markdown(f'<div class="comment-box">', unsafe_allow_html=True)
                    st.markdown(f"**{comment.get('user', 'Unknown')}**")
                    st.markdown(comment.get('text', ''))
                    st.caption(f"🕒 {time_ago(comment.get('time', datetime.now().isoformat()))}")
                    if comment.get('user') == st.session_state.current_user:
                        if st.button("🗑️", key=f"del_comment_{post_id}_{comment_idx}"):
                            comments.pop(comment_idx)
                            update_post(post_id, {'comments': comments})
                            st.session_state.posts = get_all_posts()
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                
                comment_text = st.text_input("Write a comment...", key=f"comment_input_{post_id}")
                if st.button("Post Comment", key=f"post_comment_{post_id}"):
                    if comment_text.strip():
                        comments.append({
                            'user': st.session_state.current_user,
                            'text': comment_text,
                            'time': datetime.now().isoformat()
                        })
                        update_post(post_id, {'comments': comments})
                        if st.session_state.current_user != post.get('username'):
                            add_notification(post.get('username'), 'comment', f"{st.session_state.current_user} commented on your post", post_id)
                        st.session_state.posts = get_all_posts()
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

# ================= CREATE POST PAGE =================
def show_create_post():
    st.markdown("## ➕ Create Post")
    
    with st.form("create_form"):
        post_text = st.text_area("What's on your mind?", height=150, placeholder="Share your thoughts... Use #hashtags")
        
        media_type = st.radio("Choose media type:", ["📝 Text only", "📷 Image", "🎥 Video"], horizontal=True)
        
        image_file = None
        video_file = None
        
        if media_type == "📷 Image":
            image_file = st.file_uploader("Upload image", type=['png', 'jpg', 'jpeg', 'gif'])
        elif media_type == "🎥 Video":
            video_file = st.file_uploader("Upload video", type=['mp4', 'avi', 'mov', 'mkv', 'webm'])
        
        submitted = st.form_submit_button("📤 Post", use_container_width=True)
        
        if submitted and post_text.strip():
            img_bytes = None
            vid_bytes = None
            
            if image_file:
                img_bytes = base64.b64encode(image_file.read()).decode('utf-8')
            if video_file:
                vid_bytes = base64.b64encode(video_file.read()).decode('utf-8')
            
            new_post = {
                'id': str(uuid.uuid4()),
                'username': st.session_state.current_user,
                'text': post_text,
                'image': img_bytes,
                'video': vid_bytes,
                'media_type': media_type,
                'liked_by': [],
                'comments': [],
                'shares': 0,
                'original_post': None,
                'created_at': datetime.now().isoformat()
            }
            
            success, _ = create_post(new_post)
            if success:
                st.success("Posted successfully!")
                st.session_state.posts = get_all_posts()
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error("Failed to post")
                try:
                   success, _ = create_post(new_post)
                   if success:
                       st.success("Posted!")
                   else:
                       st.error(f"Failed: {_}")
                       st.code(str(_))
                except Exception as e:
                   st.error(f"Error: {e}")
                   st.code(traceback.format_exc())

# ================= PROFILE PAGE =================
def show_profile():
    st.markdown("## 👤 My Profile")
    
    current_user = st.session_state.current_user
    user_data = get_user(current_user)
    
    if not user_data:
        st.error("User not found")
        return
    
    following = user_data.get('following', [])
    followers_count = len([u for u in st.session_state.users if current_user in u.get('followers', [])])
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("👤")
    with col2:
        st.markdown(f"### {current_user}")
        if user_data.get('bio'):
            st.caption(f"📝 {user_data['bio']}")
    
    col1, col2, col3, col4 = st.columns(4)
    my_posts = [p for p in st.session_state.posts if p.get('username') == current_user]
    total_likes = sum(len(p.get('liked_by', [])) for p in my_posts)
    
    with col1:
        st.metric("Posts", len(my_posts))
    with col2:
        st.metric("Following", len(following))
    with col3:
        st.metric("Followers", followers_count)
    with col4:
        st.metric("Total Likes", total_likes)
    
    st.markdown("---")
    st.markdown("### My Posts")
    
    for post in my_posts:
        with st.container():
            st.markdown(f'<div class="post-card">', unsafe_allow_html=True)
            st.write(post.get('text', ''))
            if post.get('image'):
                try:
                    img_bytes = base64.b64decode(post['image'])
                    st.image(img_bytes, width=200)
                except:
                    pass
            st.write(f"❤️ {len(post.get('liked_by', []))} likes | 💬 {len(post.get('comments', []))} comments")
            st.markdown('</div>', unsafe_allow_html=True)

# ================= FIND USERS PAGE =================
def show_find_users():
    st.markdown("## 🔍 Find Users")
    
    search = st.text_input("Search by username")
    current_user = st.session_state.current_user
    user_data = get_user(current_user)
    following = user_data.get('following', []) if user_data else []
    
    for user_obj in st.session_state.users:
        username = user_obj.get('username')
        if username == current_user:
            continue
        if search and search.lower() not in username.lower():
            continue
        
        col1, col2, col3 = st.columns([1, 3, 2])
        with col1:
            st.write("👤")
        with col2:
            st.write(f"**{username}**")
        with col3:
            is_following = username in following
            if st.button("Unfollow" if is_following else "Follow", key=f"follow_{username}"):
                if is_following:
                    unfollow_user(current_user, username)
                else:
                    follow_user(current_user, username)
                st.session_state.users = get_all_users()
                st.rerun()

# ================= MAIN APP =================
def main():
    if not st.session_state.logged_in:
        show_login()
    else:
        # Sidebar
        with st.sidebar:
            st.markdown(f"### 👤 {st.session_state.current_user}")
            st.markdown("---")
            
            pages = {
                "🏠 Home": "home",
                "➕ Create Post": "create",
                "👤 My Profile": "profile",
                "🔍 Find Users": "find",
            }
            
            for label, page in pages.items():
                if st.button(label, use_container_width=True):
                    st.session_state.page = page
                    st.rerun()
            
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.rerun()
        
        # Page routing
        if st.session_state.page == "home":
            show_home()
        elif st.session_state.page == "create":
            show_create_post()
        elif st.session_state.page == "profile":
            show_profile()
        elif st.session_state.page == "find":
            show_find_users()

if __name__ == "__main__":
    main()
