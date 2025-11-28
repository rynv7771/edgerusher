from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('NEXT_PUBLIC_SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

print("Deleting old games...")
supabase.table('ai_outputs').delete().neq('id', 0).execute()
supabase.table('games_raw').delete().neq('id', 0).execute()
print("✅ Old data cleared")
