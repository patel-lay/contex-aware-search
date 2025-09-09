#Read the document and parse it make it ready for indexing. 
import os 

#main file

from metaflow import FlowSpec, step, IncludeFile, Parameter
from index import load_docs
from langchain_ollama import OllamaEmbeddings
import redis

class query_flow(FlowSpec):
    question = Parameter("question", default="What is metaflow")

    @step
    def start(self):
        self.docs = []
        self.next(load_doc)

    @step
    def load_doc(self):
        self.docs = load_docs(repo_path)
        self.next(self.embed_doc)

    @step
    def embed_doc(self):
        embeddings = OllamaEmbeddings(model="llama3") # Replace "llama3" with your chosen model
        texts_to_embed = [d["content"] for d in self.docs] # Extract the text from each dictionary
        document_embeddings = embeddings.embed_documents(texts_to_embed)
        for i, d in enumerate(self.docs):
            d["embedding"] = document_embeddings[i]
            
        self.next(self.write_to_redis)
    
    def load_docs(repo_path):
        # docs = []
        for path, _ , files in os.walk(repo_path):
            for file in files:
                if f.endswith((".md")):
                    with open(os.path.join(path, f), "r", encoding="utf-8") as fh:
                        self.docs.append({
                            "path": os.path.join(root, f)}, 
                            "content": fh.read())


    @step
    def write_to_redis(self):
        r = redis.Redis(
            host= "localhost",
            port = 6379,
            decode_response = False)

        for idx, doc in enumerate(self.docs):
            key = f"doc:{doc['repo']}.{idx}"
            r.hset(key, mapping = {
                "path": doc[path],
                "content": doc["content"],
                "embedding": doc["embedding"]
            })
        self.next(end)

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



    

    
