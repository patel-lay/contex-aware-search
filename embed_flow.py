#Read the document and parse it make it ready for indexing. 
import os 

#main file

from metaflow import FlowSpec, step, IncludeFile, Parameter
from langchain_ollama import OllamaEmbeddings
import redis
import numpy as np

class embed_flow(FlowSpec):
    # repo_path = Parameter("repo", default="/Users/laypatel/Documents/projects/metaflow")

    @step
    def start(self):
        self.repo_path = "/Users/laypatel/Documents/projects/metaflow/docs"
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
                        self.docs.append({
                            "repo" : "metaflow",
                            "path": os.path.join(path, f), 
                            "content": fh.read()})


    @step
    def write_to_redis(self):
        r = redis.Redis(
            host= "localhost",
            port = 6379,
            decode_responses = False)
        print("Entering redis here")

        for idx, doc in enumerate(self.docs):
            key = f"doc:{doc['repo']}.{idx}"
            r.hset(key, mapping = {
                "path": doc["path"],
                "content": doc["content"],
                "embedding": doc["embedding"]
            })
        self.next(self.end)

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


    

    
