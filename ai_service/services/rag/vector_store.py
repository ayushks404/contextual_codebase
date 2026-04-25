import faiss
import os
import pickle
import numpy as np
from supabase_client import upload_index, download_index

VECTOR_SIZE = 384
LOCAL_INDEX_PATH = "./tmp/index.faiss"
LOCAL_META_PATH = "./tmp/meta.pkl"


#fixed race condition
def save_index(project_id: str, vectors, metadata):
    os.makedirs("./tmp", exist_ok=True)
    
    # Each project gets its OWN file — namespace by project_id
    faiss_path = f"./tmp/{project_id}.faiss"
    meta_path = f"./tmp/{project_id}.meta"
    
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    
    faiss.write_index(index, faiss_path)
    
    with open(meta_path, "wb") as f:
        pickle.dump(metadata, f)

def load_index(project_id: str):
    faiss_path = f"./tmp/{project_id}.faiss"
    meta_path = f"./tmp/{project_id}.meta"
    
    if not os.path.exists(faiss_path):
        raise FileNotFoundError(f"No index found for project {project_id}. Index it first.")
    
    index = faiss.read_index(faiss_path)
    
    with open(meta_path, "rb") as f:
        metadata = pickle.load(f)
    
    return index, metadata