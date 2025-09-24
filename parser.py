#Read the document and parse it make it ready for indexing. 
import os 
import sys
from metaflow import FlowSpec, step, IncludeFile, Parameter

import redis
import numpy as np
import re
from services.embedder import embed_and_write
from parsers.markdown_parser import markdown_parser
from parsers.web_crawler import scrape_web_docs

class parser_flow(FlowSpec):
    # repo_path = Parameter("repo", default="/Users/laypatel/Documents/projects/metaflow")

    @step
    def start(self):
        self.repo_path = "/Users/laypatel/Documents/projects/metaflow"
        self.web_path = "https://docs.metaflow.org/"
        self.max_iter = 30
        self.docs = []
        self.next(self.load_doc)

    @step
    def load_doc(self):
        self.docs+=markdown_parser(self.docs, self.repo_path)
        self.next(self.load_web_doc)
    
    @step
    def load_web_doc(self):
        self.docs+=scrape_web_docs(self.web_path, self.max_iter)
        self.next(self.embed_doc)


    @step
    def embed_doc(self):
        embed_and_write(self.docs)       
        self.next(self.end) 

    @step
    def end(self):
        print("Documents read and indexed")
        #End the call


if __name__ == "__main__":
    parser_flow()


    

    
