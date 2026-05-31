    with st.sidebar:
        # Profile section with avatar
        col1, col2 = st.columns([1, 3])
        with col1:
            if user_data.get('image'):
                try:
                    st.image(base64.b64decode(user_data['image']), width=50)
                except:
                    st.write("👤")
            else:
                st.write("👤")
        with col2:
            st.markdown(f"### {current_user}")
        
        st.markdown(f"**👥 Following:** {len(following)}")
        st.markdown(f"**⭐ Followers:** {followers}")
        
        if user_data.get('bio'):
            st.caption(f"📝 {user_data['bio'][:50]}...")
        
        st.markdown("---")
        
        # Navigation
        nav_items = {
            "🏠 Home": "home",
            "➕ Create Post": "create",
            "👤 My Profile": "profile",
            "🔍 Search Posts": "search",
            "📊 Analytics": "analytics",
            "💾 Saved Posts": "saved",
            "🔍 Find Users": "find",
            "🏷️ Trending": "trending"
        }
        
        for label, page in nav_items.items():
            if st.button(label, use_container_width=True):
                st.session_state.page = page
                st.session_state.edit_post_id = None
                st.rerun()
        
        notif_label = f"🔔 Notifications ({unread_count})" if unread_count > 0 else "🔔 Notifications"
        if st.button(notif_label, use_container_width=True):
            st.session_state.page = "notifications"
            st.rerun()
        
        st.markdown("---")
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.page = "edit_profile"
            st.rerun()
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
