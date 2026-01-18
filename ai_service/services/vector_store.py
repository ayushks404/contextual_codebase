import faiss
import os
import pickle
import numpy as np
from supabase_client import upload_index, download_index

VECTOR_SIZE = 384
LOCAL_INDEX_PATH = "./tmp/index.faiss"
LOCAL_META_PATH = "./tmp/meta.pkl"

def save_index(project_id: str, vectors: np.ndarray, metadata: list):
    os.makedirs("./tmp", exist_ok=True)

    n, dim = vectors.shape
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    faiss.write_index(index, LOCAL_INDEX_PATH)

    with open(LOCAL_META_PATH, "wb") as f:
        pickle.dump(metadata, f)

    upload_index(LOCAL_INDEX_PATH, f"{project_id}.faiss")
    upload_index(LOCAL_META_PATH, f"{project_id}.meta")


def load_index(project_id: str):
    os.makedirs("./tmp", exist_ok=True)

    download_index(f"{project_id}.faiss", LOCAL_INDEX_PATH)
    download_index(f"{project_id}.meta", LOCAL_META_PATH)

    index = faiss.read_index(LOCAL_INDEX_PATH)

    with open(LOCAL_META_PATH, "rb") as f:
        metadata = pickle.load(f)

    return index, metadata