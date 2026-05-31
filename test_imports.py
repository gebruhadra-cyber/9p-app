# Test all imports
try:
    import streamlit as st
    print("✅ streamlit")
except Exception as e:
    print(f"❌ streamlit: {e}")

try:
    from supabase import create_client
    print("✅ supabase")
except Exception as e:
    print(f"❌ supabase: {e}")

try:
    from dotenv import load_dotenv
    print("✅ python-dotenv")
except Exception as e:
    print(f"❌ python-dotenv: {e}")

try:
    from PIL import Image
    print("✅ pillow")
except Exception as e:
    print(f"❌ pillow: {e}")

try:
    import cv2
    print("✅ opencv-python-headless")
except Exception as e:
    print(f"❌ opencv-python-headless: {e}")

try:
    import multipart
    print("✅ python-multipart")
except Exception as e:
    print(f"❌ python-multipart: {e}")

print("\n🎯 All imports checked!")
