from supabase import create_client
from datetime import datetime
import uuid

URL = "https://pobnwbzcntlfozqpbgmj.supabase.co"
KEY = "sb_publishable_btEddg2V38fI_EOYcbNrKQ_Ur9_tlt8"

supabase = create_client(URL, KEY)

# Test creating a post
test_post = {
    'id': str(uuid.uuid4()),
    'username': 'zab',  # Use your actual username
    'text': 'Hello from test!',
    'liked_by': [],
    'comments': [],
    'shares': 0,
    'created_at': datetime.now().isoformat()
}

try:
    result = supabase.table('posts').insert(test_post).execute()
    print("✅ Post created successfully!")
    print(f"   Post ID: {test_post['id']}")
    
    # Clean up
    supabase.table('posts').delete().eq('id', test_post['id']).execute()
    print("✅ Test post cleaned up")
except Exception as e:
    print(f"❌ Error: {e}")
