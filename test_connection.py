from supabase import create_client

# Your configuration
URL = "https://pobnwbzcntlfozqpbgmj.supabase.co"
KEY = "sb_publishable_btEddg2V38fI_EOYcbNrKQ_Ur9_tlt8"

print("🔌 Testing Supabase connection...")
print(f"URL: {URL}")
print(f"Key: {KEY[:20]}...")  # Only show first 20 chars for security

try:
    supabase = create_client(URL, KEY)
    
    # Try to get users (this will work even if table is empty)
    result = supabase.table('users').select('*').limit(1).execute()
    
    print("✅ SUCCESS! Connected to Supabase!")
    print(f"📊 Found {len(result.data)} users in database")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nPossible issues:")
    print("1. Tables not created yet - run SQL queries in Supabase SQL Editor")
    print("2. Network issue - check your internet")
