import requests
import numpy as np
import os

STAPI_URL = os.getenv("STAPI_URL", "http://stapi:8080/v1/embeddings")

def generate_embeddings(texts):
    

    if isinstance(texts, str):
        texts = [texts]
    
    response = requests.post(
        STAPI_URL,
        headers={"Content-Type": "application/json"},
        json={
            "input": texts,
            "model": "all-MiniLM-L6-v2"
        },
        timeout=60
    )

    if response.status_code != 200:
        raise Exception(f"STAPI error: {response.text}")


    vectors = [item["embedding"] for item in response.json()["data"]]
    return np.array(vectors, dtype="float32")

