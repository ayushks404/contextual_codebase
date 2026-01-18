from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import shutil
import os
import stat
import time
from services.rag_engine import index_repo, answer_question


app = FastAPI(title="CCA AI Service")

#Models

class IndexRequest(BaseModel):
    project_id: str
    repo_url: str

class QueryRequest(BaseModel):
    project_id: str
    question: str

#Routes



#checking is api works ?
@app.get("/health")
def health():
    return {"status": "ok"}


#indexing of the repo
@app.post("/index-repo")
def index_repository(req: IndexRequest):
    try:
        result = index_repo(req.project_id, req.repo_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#query route
@app.post("/query")
def query_repository(req: QueryRequest):
    try:
        result = answer_question(req.project_id, req.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



#delete the data of user after logged out


def force_delete(func, path, exc_info):
    # Change file permission and retry
    os.chmod(path, stat.S_IWRITE)
    func(path)


from supabase_client import delete_index

TMP_REPO_PATH = "./tmp/repos"
LOCAL_INDEX_PATH = "./tmp/index.faiss"
LOCAL_META_PATH = "./tmp/meta.pkl"

@app.post("/cleanup")
def cleanup_repo(data: dict):
    project_id = data["project_id"]

    # 1. Delete from Supabase
    try:
        delete_index(f"{project_id}.faiss")
        delete_index(f"{project_id}.meta")
    except Exception as e:
        print("Supabase delete error:", e)

    # Delete cloned repo (Windows-safe)
    repo_path = os.path.join(TMP_REPO_PATH, project_id)
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=force_delete)

    # Delete FAISS temp files
    if os.path.exists(LOCAL_INDEX_PATH):
        os.remove(LOCAL_INDEX_PATH)

    if os.path.exists(LOCAL_META_PATH):
        os.remove(LOCAL_META_PATH)


    return {"status": "deleted"}