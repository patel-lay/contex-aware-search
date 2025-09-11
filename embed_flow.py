#Read the document and parse it make it ready for indexing. 
import os 

#main file

from metaflow import FlowSpec, step, IncludeFile, Parameter
from langchain_ollama import OllamaEmbeddings
import redis
import numpy as np
import re
class embed_flow(FlowSpec):
    # repo_path = Parameter("repo", default="/Users/laypatel/Documents/projects/metaflow")

    @step
    def start(self):
        self.repo_path = "/Users/laypatel/Documents/projects/metaflow"
        self.docs = []
        self.next(self.load_doc)

    @step
    def load_doc(self):
        self.load_docs(self.repo_path)
        self.next(self.embed_doc)

    @step
    def embed_doc(self):
        embeddings = OllamaEmbeddings(model="llama3.2") # Replace "llama3" with your chosen model
        texts_to_embed = [d["content"] for d in self.docs] # Extract the text from each dictionary
        document_embeddings = embeddings.embed_documents(texts_to_embed)
        for i, d in enumerate(self.docs):
            d["embedding"] = np.array(document_embeddings[i], dtype=np.float32).tobytes()
            
        self.next(self.write_to_redis)
    
    def load_docs(self, repo_path):
        # docs = []
        for path, _ , files in os.walk(repo_path):
            for f in files:
                if f.endswith((".md")):
                    with open(os.path.join(path, f), "r", encoding="utf-8") as fh:
                        full_path = os.path.join(path, f)
                        self.prepare_chunks(fh.read(), full_path)
 

    @step
    def write_to_redis(self):
        r = redis.Redis(
            host= "localhost",
            port = 6379,
            decode_responses = False)

        for idx, doc in enumerate(self.docs):
            key = f"doc:{doc['repo']}:sec:{doc['section_id']}:chunk:{doc['chunk_id']}"
            # key = f"doc:{doc['repo']}.{idx}"
            r.hset(key, mapping = {
                "path": doc["path"],
                "content": doc["content"],
                "embedding": doc["embedding"],
                "section_id": doc["embedding"],
                "chunk_id": doc["embedding"]
                })
        self.next(self.end)

    def prepare_chunks(self, markdown_text, path):
        sections = self.split_markdown_sections(markdown_text)
        for i, sec in enumerate(sections):
            sec_chunks = self.chunk_text(sec)
            for j, chunk in enumerate(sec_chunks):
                self.docs.append({
                    "repo": "metaflow",
                    "path": path,
                    "section_id": i,
                    "chunk_id": j,
                    "content": chunk
                })


    def split_markdown_sections(self, text: str):
        sections = re.split(r"\n(?=#)", text)  # split on headers starting with "#"
        return [s.strip() for s in sections if s.strip()]

    def chunk_text(self, text, chunk_size=500, overlap=50):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i+chunk_size])
            chunks.append(chunk)
        return chunks

    # @step 
    # def index_code(self):
    #     self.next(self.join)

    # @step
    # def join(self, index):
    #     #merge both the index
    #     #save it into the DB

    @step
    def end(self):
        print("Documents read and indexed")
        #End the call


if __name__ == "__main__":
    embed_flow()


    

    
