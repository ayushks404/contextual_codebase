# services/rag_engine.py
import os
from services.rag.repo_cloner import clone_repo
from services.rag.chunker import read_files, chunk_code
from services.rag.embeddings import generate_embeddings
from services.rag.vector_store import save_index, load_index
from services.llm.llm_client import generate


def index_repo(project_id: str, repo_url: str):
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

    vectors = generate_embeddings(chunks)  
    save_index(project_id, vectors, metadata)

    return {"status": "indexed", "files": len(files), "chunks": len(chunks)}


def answer_question(project_id: str, question: str, k: int = 5):
    index, metadata = load_index(project_id)
    query_vector = generate_embeddings([question])

    D, I = index.search(query_vector, k)

    context_blocks = []
    sources = []

    for idx in I[0]:
        if idx < 0 or idx >= len(metadata):
            continue

        file = metadata[idx]["file"]
        code = metadata[idx]["content"]

        context_blocks.append(f"""
File: {file}

Code:
{code}
------------------------------
""")

        sources.append({"file": file})

    context = "\n".join(context_blocks)

    prompt = f"""
You are a senior software engineer and codebase analyst.

You are allowed to quote and explain the code.

When showing code:
- Always use markdown code blocks
- Mention the filename above the code

Respond in clean markdown format using headings, bullets, and code blocks.

Code Context:
{context}

Question:
{question}
"""

    answer = generate(prompt)

    return {
        "answer": answer,
        
    }
