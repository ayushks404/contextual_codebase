# from dotenv import load_dotenv
# load_dotenv()

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import shutil
# import os
# import stat
# import time
# from services.rag.rag_engine import index_repo, answer_question
# from services.agents.critic import critic_agent
# from services.ml.feature_extractor import extract_features
# from services.ml.model import predict_confidence

# app = FastAPI(title="CCA AI Service")

# #Models

# class IndexRequest(BaseModel):
#     project_id: str
#     repo_url: str

# class QueryRequest(BaseModel):
#     project_id: str
#     question: str

# #Routes



# #checking is api works ?
# @app.get("/health")
# def health():
#     return {"status": "ok"}


# #indexing of the repo
# @app.post("/index-repo")
# def index_repository(req: IndexRequest):
#     try:
#         result = index_repo(req.project_id, req.repo_url)
#         return result
#     except Exception as e:
#         print("🔥 INDEX ERROR:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/query")
# def query_repository(req: QueryRequest):
#     try:
#         state = {
#             "project_id": req.project_id,
#             "query": req.question,
#             "original_query": req.question,
#             "iterations": 0
#         }

#         trace = []

#         while True:
#             # Step 1: Generate answer (your existing system)
#             result = answer_question(state["project_id"], state["query"])
#             answer = result.get("answer")

#             state["answer"] = answer

#             # Step 2: Extract features
#             features_data = extract_features({
#                 "query": state["query"],
#                 "answer": state["answer"],
#                 "docs": []  # still no context returned
#             })

#             features = features_data["features"]
#             state["features"] = features

#             # Step 3: Predict confidence
#             confidence = predict_confidence(features)
#             state["confidence"] = confidence

#             # Step 4: Critic decision
#             decision = critic_agent(state)
            
#             print(f"[Iteration {state['iterations']}] Confidence: {confidence}, Decision: {decision['action']}")

#             trace.append({
#                 "iteration": state["iterations"],
#                 "confidence": confidence,
#                 "decision": decision["action"]
#             })


#             if decision["action"] == "retry":
#                 state["query"] = f"""
#             Improve the previous answer.

#             Original Question:
#             {state["query"]}

#             Previous Answer:
#             {state["answer"]}

#             Provide a more accurate and detailed explanation using code references.
#             """

#             if decision["action"] == "accept":
#                 break

#             state["iterations"] = decision["iterations"]

#         return {
#             "answer": state["answer"],
#             "confidence": state["confidence"],
#             "iterations": state["iterations"],
#             "trace": trace
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



# #delete the data of user after logged out


# def force_delete(func, path, exc_info):
#     # Change file permission and retry
#     os.chmod(path, stat.S_IWRITE)
#     func(path)


# from supabase_client import delete_index

# TMP_REPO_PATH = "./tmp/repos"
# LOCAL_INDEX_PATH = "./tmp/index.faiss"
# LOCAL_META_PATH = "./tmp/meta.pkl"

# @app.post("/cleanup")
# def cleanup_repo(data: dict):
#     project_id = data["project_id"]

#     # 1. Delete from Supabase
#     try:
#         delete_index(f"{project_id}.faiss")
#         delete_index(f"{project_id}.meta")
#     except Exception as e:
#         print("Supabase delete error:", e)

#     # Delete cloned repo (Windows-safe)
#     repo_path = os.path.join(TMP_REPO_PATH, project_id)
#     if os.path.exists(repo_path):
#         shutil.rmtree(repo_path, onerror=force_delete)

#     # Delete FAISS temp files
#     if os.path.exists(LOCAL_INDEX_PATH):
#         os.remove(LOCAL_INDEX_PATH)

#     if os.path.exists(LOCAL_META_PATH):
#         os.remove(LOCAL_META_PATH)


#     return {"status": "deleted"}

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import shutil
import os
import stat

# Core services
from services.rag.rag_engine import index_repo, answer_question

# ML + Agents
from services.ml.feature_extractor import extract_features
from services.ml.model import predict_confidence
from services.agents.critic import critic_agent

# Optional logging
import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="CCA AI Service")


# =========================
# Models
# =========================

class IndexRequest(BaseModel):
    project_id: str
    repo_url: str

class QueryRequest(BaseModel):
    project_id: str
    question: str


# =========================
# Health Check
# =========================

@app.get("/health")
def health():
    return {"status": "ok"}


# =========================
# Index Repo
# =========================

@app.post("/index-repo")
def index_repository(req: IndexRequest):
    try:
        result = index_repo(req.project_id, req.repo_url)
        return result
    except Exception as e:
        print("🔥 INDEX ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Query with Agent Loop
# =========================

@app.post("/query")
def query_repository(req: QueryRequest):
    try:
        MAX_ITERATIONS = 5

        state = {
            "project_id": req.project_id,
            "query": req.question,
            "original_query": req.question,
            "iterations": 0
        }

        trace = []

        while state["iterations"] < MAX_ITERATIONS:

            # Step 1: Generate answer
            result = answer_question(state["project_id"], state["query"])
            answer = result.get("answer")

            state["answer"] = answer

            # Step 2: Extract features (use ORIGINAL query)
            features_data = extract_features({
                "query": state["original_query"],
                "answer": state["answer"],
                "docs": []
            })

            features = features_data["features"]

            # Step 3: Predict confidence
            confidence = predict_confidence(features)
            state["confidence"] = confidence

            # Step 4: Critic decision
            decision = critic_agent(state)

            # Logging
            logging.info(
                f"[Iteration {state['iterations']}] "
                f"Confidence: {confidence}, Decision: {decision['action']}"
            )

            # Trace for API response
            trace.append({
                "iteration": state["iterations"],
                "confidence": confidence,
                "decision": decision["action"]
            })

            # Stop if good
            if decision["action"] == "accept":
                break

            # 🔥 Improve query using previous answer
            state["query"] = f"""
Original Question:
{state["original_query"]}

Previous Answer:
{state["answer"]}

Improve the answer with:
- better accuracy
- clearer explanation
- relevant code references
"""

            # Increment iteration
            state["iterations"] += 1

        # Final response
        return {
            "answer": state["answer"],
            "confidence": state["confidence"],
            "iterations": state["iterations"],
            "trace": trace
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Cleanup
# =========================

def force_delete(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


from supabase_client import delete_index

TMP_REPO_PATH = "./tmp/repos"
LOCAL_INDEX_PATH = "./tmp/index.faiss"
LOCAL_META_PATH = "./tmp/meta.pkl"


@app.post("/cleanup")
def cleanup_repo(data: dict):
    project_id = data["project_id"]

    # Delete from Supabase (optional)
    try:
        delete_index(f"{project_id}.faiss")
        delete_index(f"{project_id}.meta")
    except Exception as e:
        print("Supabase delete error:", e)

    # Delete repo
    repo_path = os.path.join(TMP_REPO_PATH, project_id)
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=force_delete)

    # Delete temp files
    if os.path.exists(LOCAL_INDEX_PATH):
        os.remove(LOCAL_INDEX_PATH)

    if os.path.exists(LOCAL_META_PATH):
        os.remove(LOCAL_META_PATH)

    return {"status": "deleted"}