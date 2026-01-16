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

@app.post("/cleanup")
def cleanup_repo(data: dict):
    project_id = data["project_id"]

    repo_path = f"./storage/repos/{project_id}"
    index_path = f"./storage/indexes/{project_id}.index"
    meta_path = f"./storage/indexes/{project_id}.meta"

    # wait a moment to let git release file handles
    time.sleep(1)

    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=force_delete)

    if os.path.exists(index_path):
        os.remove(index_path)

    if os.path.exists(meta_path):
        os.remove(meta_path)

    return {"status": "deleted"}
