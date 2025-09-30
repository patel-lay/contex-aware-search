# query_api.py
from fastapi import FastAPI, Query, Body
import redis
import numpy as np
from langchain_ollama import OllamaEmbeddings
from langchain.docstore.document import Document as langChainDocument
from langchain.chains import load_summarize_chain
from langchain_community.llms import Ollama
from collections import defaultdict
from crud.document import retrive_document
from models import Document


llm = Ollama(model="llama3.2")
 

def group_by_source(docs):
    grouped = defaultdict(list)
    for doc in docs:
        grouped[doc.metadata["path"]].append(doc.page_content)
    
    merged = []
    for source, contents in grouped.items():
        merged.append({
            "path": source,
            "chunk": "\n".join(contents)
        })
    return merged

def summarize_agent(raw_result):
    docs = [langChainDocument(page_content=r.chunk, metadata={"path": r.source})
        for r in raw_result]

    grouped_docs = group_by_source(docs)
    print(docs)
    prompt = f"""
        You are an assistant summarizing technical documentation. 
        Use only the provided text as your source. 
        For every statement you make, include the citation in the format: [Source: <path>].  
        If no relevant source is found, respond with: "No relevant information available."    

        Documentation:
        {grouped_docs}
    """

    chain = load_summarize_chain(llm, chain_type="stuff")
    summary = chain.run([langChainDocument(page_content=prompt)])

    return summary


app = FastAPI(title="Query API with Ollama Embeddings")

# Redis connection
r = redis.Redis(host="localhost", port=6379, db=0)

# Embedding model
emb_model = OllamaEmbeddings(model="llama3.2")

def get_embedding(text: str):
    embedded_text = emb_model.embed_documents(text)
    emd = embedded_text[0][:1536]

    return emd

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def query_redis(question: str, top_k: int = 3):
    q_emb = get_embedding(question)
    results = retrive_document(q_emb, top_k)

    return summarize_agent(results)

@app.get("/query")
def query(question: str = Body(..., description="Your question")):
    results = query_redis(question, 3)
    return {"question": question, "results": results}

# Run: uvicorn query_api:app --reload --port 8000
