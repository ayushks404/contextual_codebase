from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_index(local_path, remote_name):
    try:
        delete_index(remote_name)
    except:
        pass
        
    with open(local_path, "rb") as f:
        supabase.storage.from_(SUPABASE_BUCKET).upload(remote_name, f)

def download_index(remote_name, local_path):
    data = supabase.storage.from_(SUPABASE_BUCKET).download(remote_name)
    with open(local_path, "wb") as f:
        f.write(data)

def delete_index(remote_name):
    supabase.storage.from_(SUPABASE_BUCKET).remove([remote_name])
print("SUPABASE_URL:", SUPABASE_URL)
