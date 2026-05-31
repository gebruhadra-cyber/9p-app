import streamlit as st

print("Testing secrets...")
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_PUBLISHABLE_KEY"]
    print("✅ Secrets found!")
    print(f"URL: {url}")
    print(f"Key: {key[:20]}...")
except Exception as e:
    print(f"❌ Error: {e}")
