# query_api.py
from fastapi import FastAPI, Query, Body
import redis
import numpy as np
from langchain_ollama import OllamaEmbeddings
from langchain.docstore.document import Document
from langchain.chains import load_summarize_chain
from langchain_community.llms import Ollama

llm = Ollama(model="llama3.2")
 
def summarize_agent(raw_result):
    docs = [Document(page_content=r["content"], metadata={"citation": r["citation"], "score": r["score"]})
        for r in raw_result]

    docs_text = "\n\n".join([f"[Source: {d.metadata['citation']}] {d.page_content}" for d in docs])

    prompt = f"""
    Summarize the following documentation. 
    Include citations by referencing the [Source] provided.

    {docs_text}
    """

    chain = load_summarize_chain(llm, chain_type="stuff")
    summary = chain.run([Document(page_content=prompt)])

    return summary


app = FastAPI(title="Query API with Ollama Embeddings")

# Redis connection
r = redis.Redis(host="localhost", port=6379, db=0)

# Embedding model
emb_model = OllamaEmbeddings(model="llama3.2")

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
            text = data[b"content"].decode("utf-8")
            score = cosine_similarity(q_emb, emb)
            path = data[b"path"].decode("utf-8")
            results.append({"content": text, "score": float(score), "citation": path})
    results.sort(key=lambda x: x["score"], reverse=True)
    return summarize_agent(results[:top_k])

@app.get("/query")
def query(question: str = Body(..., description="Your question")):
    results = query_redis(question, 3)
    return {"question": question, "results": results}

# Run: uvicorn query_api:app --reload --port 8000
