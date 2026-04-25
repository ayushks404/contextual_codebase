import os
from typing import List

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200

def read_files(repo_path: str) -> List[str]:
    """Return list of source file paths (skip node_modules and .git)."""
    files = []

    for root, dirs, filenames in os.walk(repo_path):
        if "node_modules" in root or ".git" in root :
            continue

        for file in filenames:
            if file.endswith((".js", ".ts", ".py", ".java", ".cpp", ".c", ".md")):
                files.append(os.path.join(root, file))
    
    return files



def chunk_code(file_path: str, chunk_size: int = 50, overlap: int = 10) -> List[str]:
    """
    Chunk by LINES not characters.
    chunk_size = number of lines per chunk
    overlap = lines shared between consecutive chunks
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    if not lines:
        return []

    chunks = []
    start = 0
    total_lines = len(lines)

    while start < total_lines:
        end = min(start + chunk_size, total_lines)
        chunk = "".join(lines[start:end])
        
        if chunk.strip():  # skip empty chunks
            chunks.append(chunk)
        
        # Move forward by (chunk_size - overlap) — this is correct overlap logic
        start += chunk_size - overlap

    return chunks