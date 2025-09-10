#main file

from metaflow import FlowSpec, step, IncludeFile, Parameter
from langchain_ollama import OllamaEmbeddings
import redis
import subprocess

class context_aware_agent(FlowSpec):

    @step
    def start(self):
        self.docs = []
        self.next(self.embed_and_index)

    @step
    def embed_and_index(self):
        subprocess.run(["python3", "embed_flow.py", "run", "--repo", "/Users/laypatel/Documents/projects/metaflow"])
        self.next(self.end)
    
    # @step
    # def query(self):
    #     #read rest api and get the question, or maybe a socket connection?
    #     #keep it open till the connection is open
    #     q = "How does retyr works in Metaflow?"

    #     # subprocess.run(["python3", "query_flow.py", "run", "--question", "q"])
    #     self.next(self.end)

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
    context_aware_agent()