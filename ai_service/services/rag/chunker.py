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

def chunk_code(file_path: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> List[str]:
    """Return list of text chunks for a single file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    if not text:
        return []

    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = max(end - overlap, end) if overlap < chunk_size else end
    return chunks