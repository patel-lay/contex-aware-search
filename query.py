# query_api.py
from fastapi import FastAPI, Query
import redis
import numpy as np
from langchain_community.embeddings import OllamaEmbeddings

app = FastAPI(title="Query API with Ollama Embeddings")

# Redis connection
r = redis.Redis(host="localhost", port=6379, db=0)

# Embedding model
emb_model = OllamaEmbeddings(model="nomic-embed-text")

def get_embedding(text: str):
    return np.array(emb_model.embed_query(text), dtype=np.float32)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def query_redis(question: str, top_k: int = 3):
    q_emb = get_embedding(question)
    results = []
    for key in r.scan_iter():
        data = r.hgetall(key)
        if b"embedding" in data:
            emb = np.frombuffer(data[b"embedding"], dtype=np.float32)
            text = data[b"text"].decode("utf-8")
            score = cosine_similarity(q_emb, emb)
            results.append({"text": text, "score": float(score)})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

@app.get("/query")
def query_api(question: str = Query(..., description="Your question")):
    results = query_redis(question)
    return {"question": question, "results": results}

# Run: uvicorn query_api:app --reload --port 8000
