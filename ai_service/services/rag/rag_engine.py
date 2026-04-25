import os
import numpy as np
from services.rag.repo_cloner import clone_repo
from services.rag.chunker import read_files, chunk_code
from services.rag.embeddings import generate_embeddings
from services.rag.vector_store import save_index, load_index
from services.llm.llm_client import generate


def index_repo(project_id: str, repo_url: str) -> dict:
    """
    Full indexing pipeline for a GitHub repo.

    Steps:
    1. Clone repo to ./tmp/repos/<project_id>/
    2. Read all supported code files
    3. Chunk each file by lines with overlap (so context isn't lost at boundaries)
    4. Generate sentence-transformer embeddings for every chunk
    5. Save FAISS index + metadata — namespaced by project_id

    Returns stats so the backend knows indexing succeeded.
    """
    repo_path = clone_repo(repo_url, project_id)
    files = read_files(repo_path)

    chunks = []
    metadata = []

    for file in files:
        parts = chunk_code(file)
        for part in parts:
            chunks.append(part)
            metadata.append({
                "file": file,
                "content": part
            })

    if not chunks:
        return {"status": "no_chunks", "files": len(files), "chunks": 0}

    vectors = generate_embeddings(chunks)   # shape: (num_chunks, 384)
    save_index(project_id, vectors, metadata)

    return {"status": "indexed", "files": len(files), "chunks": len(chunks)}


def answer_question(project_id: str, question: str, k: int = 5) -> dict:
    """
    Retrieves the top-k most relevant chunks and asks the LLM to answer.

    Returns:
        answer:            LLM-generated response in markdown
        query_vector:      Embedding of the question — shape (1, 384)
        retrieved_vectors: List of embeddings for the k retrieved chunks
                           Used by compute_confidence() in app.py to score
                           how relevant the retrieval actually was.

    Why return vectors?
    The confidence score must be computed OUTSIDE this function
    so the agentic loop in app.py can decide whether to retry.
    We don't hardcode that decision here — separation of concerns.
    """
    index, metadata = load_index(project_id)

    # Embed the question — same model as indexing, so vectors are in the same space
    query_vector = generate_embeddings([question])  # shape: (1, 384)

    # FAISS returns distances (D) and indices (I) of top-k nearest neighbors
    # IndexFlatL2 uses euclidean distance — lower D = more similar
    D, I = index.search(query_vector, k)

    context_blocks = []
    sources = []
    retrieved_vectors = []

    for idx in I[0]:
        # FAISS returns -1 for empty slots when index has fewer than k vectors
        if idx < 0 or idx >= len(metadata):
            continue

        file = metadata[idx]["file"]
        code = metadata[idx]["content"]
        chunk_embedding = index.reconstruct(int(idx))  # get the stored vector back

        context_blocks.append(f"File: {file}\n\nCode:\n{code}\n{'-'*30}")
        sources.append({"file": file})
        retrieved_vectors.append(chunk_embedding)   # shape: (384,)

    context = "\n".join(context_blocks)

    prompt = f"""You are a senior software engineer and codebase analyst.

When showing code:
- Always use markdown code blocks with the language name
- Mention the filename above each code block

Respond in clean markdown using headings, bullets, and code blocks.

Code Context:
{context}

Question:
{question}
"""

    answer = generate(prompt)

    return {
        "answer": answer,
        "query_vector": query_vector,            # shape (1, 384)
        "retrieved_vectors": retrieved_vectors,  # list of (384,) arrays
        "sources": sources
    }