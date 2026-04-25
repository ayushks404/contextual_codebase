from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import shutil
import os
import stat
import re
import logging

# Core RAG service — handles repo cloning, chunking, embedding, and querying
from services.rag.rag_engine import index_repo, answer_question

# Confidence scoring and critic agent for the agentic retry loop
from services.ml.model import compute_confidence
from services.agents.critic import critic_agent

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="CCA AI Service")


# =========================
# Request Models
# =========================

class IndexRequest(BaseModel):
    project_id: str
    repo_url: str

class QueryRequest(BaseModel):
    project_id: str
    question: str


# =========================
# Helpers
# =========================

def validate_github_url(url: str) -> bool:
    """
    Only allow GitHub URLs in the format:
    https://github.com/<owner>/<repo>

    This prevents attackers from passing:
    - file:///etc/passwd       (local file read via git clone)
    - https://evil.com/repo    (arbitrary remote code)
    - Internal IPs             (SSRF — hitting internal services)
    """
    pattern = r'^https://github\.com/[\w\-]+/[\w\-\.]+/?$'
    return bool(re.match(pattern, url))

def force_delete(func, path, exc_info):
    """
    Windows-safe deletion helper for shutil.rmtree.
    .git/ directories often have read-only files on Windows —
    this chmod's them writable before retrying.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


# =========================
# Health Check
# =========================

@app.get("/health")
def health():
    """Liveness probe used by Docker healthcheck and load balancers."""
    return {"status": "ok"}


# =========================
# Index Repository
# =========================

@app.post("/index-repo")
def index_repository(req: IndexRequest):
    """
    Pipeline:
    1. Validate GitHub URL (security)
    2. Clone the repo locally under ./tmp/repos/<project_id>/
    3. Read all code files, chunk by lines with overlap
    4. Generate embeddings for each chunk (sentence-transformers)
    5. Save FAISS index to ./tmp/<project_id>.faiss
       and metadata to ./tmp/<project_id>.meta

    project_id namespacing ensures users never overwrite each other's indexes.
    """
    if not validate_github_url(req.repo_url):
        raise HTTPException(
            status_code=400,
            detail="Only public GitHub URLs supported. Format: https://github.com/owner/repo"
        )

    try:
        result = index_repo(req.project_id, req.repo_url)
        return result
    except Exception as e:
        logging.error(f"Indexing failed for {req.project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Query — Agentic Retry Loop
# =========================

@app.post("/query")
def query_repository(req: QueryRequest):
    """
    Answers a natural language question about the indexed codebase.

    Agentic loop:
    - Iteration 1: RAG retrieves top-k chunks, LLM generates answer
    - Confidence is computed as cosine similarity between query embedding
      and retrieved chunk embeddings (high = relevant chunks found)
    - Critic checks: if confidence >= 0.5 → accept and return
    - If low confidence → refine the query with previous answer as context and retry
    - Max 3 iterations to cap LLM API cost
    """
    MAX_ITERATIONS = 3

    state = {
        "project_id": req.project_id,
        "query": req.question,
        "original_query": req.question,
        "iterations": 0,
        "answer": None,
        "confidence": 0.0,
    }

    trace = []

    while state["iterations"] < MAX_ITERATIONS:

        # Retrieve relevant chunks + generate answer
        # answer_question now returns query_vector and retrieved_vectors
        # so confidence can be computed from actual semantic similarity
        result = answer_question(state["project_id"], state["query"])
        state["answer"] = result["answer"]

        # Real confidence: cosine similarity of query vs retrieved chunks
        # If we retrieved irrelevant chunks, similarity is low → retry
        confidence = compute_confidence(
            query_vector=result["query_vector"],
            retrieved_vectors=result["retrieved_vectors"]
        )
        state["confidence"] = confidence

        decision = critic_agent(state)

        logging.info(
            f"[Iteration {state['iterations']}] "
            f"Confidence: {confidence:.3f} | Decision: {decision['action']}"
        )

        trace.append({
            "iteration": state["iterations"],
            "confidence": confidence,
            "decision": decision["action"]
        })

        if decision["action"] == "accept":
            break

        # Refine query: give the LLM context of what it said before
        # Always anchor to original_query so we don't drift from user's intent
        state["query"] = f"""
Original Question:
{state["original_query"]}

Previous Answer (needs improvement):
{state["answer"]}

Provide a more accurate answer with:
- Specific code references from the codebase
- Clear explanation of what the code does
- Any important edge cases missing from previous answer
"""
        state["iterations"] += 1

    return {
        "answer": state["answer"],
        "confidence": state["confidence"],
        "iterations": state["iterations"],
        "trace": trace
    }


# =========================
# Cleanup
# =========================

TMP_REPO_PATH = "./tmp/repos"

@app.post("/cleanup")
def cleanup_repo(data: dict):
    """
    Deletes all local artifacts for a project:
    - Cloned repo under ./tmp/repos/<project_id>/
    - FAISS index: ./tmp/<project_id>.faiss
    - Metadata:    ./tmp/<project_id>.meta

    Must be called when user deletes a project — otherwise disk fills up.
    """
    project_id = data.get("project_id")
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id required")

    repo_path = os.path.join(TMP_REPO_PATH, project_id)
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=force_delete)
        logging.info(f"Deleted repo: {repo_path}")

    for ext in [".faiss", ".meta"]:
        path = f"./tmp/{project_id}{ext}"
        if os.path.exists(path):
            os.remove(path)
            logging.info(f"Deleted: {path}")

    return {"status": "deleted", "project_id": project_id}