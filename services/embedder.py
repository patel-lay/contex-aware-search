from langchain_ollama import OllamaEmbeddings
import redis
import numpy as np

def embed(docs):
    embeddings = OllamaEmbeddings(model="llama3.2") # Replace "llama3" with your chosen model
    texts_to_embed = [d["content"] for d in docs] # Extract the text from each dictionary
    document_embeddings = embeddings.embed_documents(texts_to_embed)
    for i, d in enumerate(docs):
        d["embedding"] = np.array(document_embeddings[i], dtype=np.float32).tobytes()

def write_to_redis(docs):
    r = redis.Redis(
        host= "localhost",
        port = 6379,
        decode_responses = False)

    for idx, doc in enumerate(docs):
        key = f"doc:{doc['repo']}:sec:{doc['section_id']}:chunk:{doc['chunk_id']}"
        # key = f"doc:{doc['repo']}.{idx}"
        r.hset(key, mapping = {
            "path": doc["path"],
            "content": doc["content"],
            "embedding": doc["embedding"],
            "section_id": doc["section_id"],
            "chunk_id": doc["chunk_id"]
            })

def embed_and_write(docs):
    embed(docs)
    write_to_redis(docs)
    
