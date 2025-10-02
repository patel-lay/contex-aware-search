#Read the document and parse it make it ready for indexing. 
import os 
import sys
from metaflow import FlowSpec, step, IncludeFile, Parameter, Config
from pydantic import BaseModel, ValidationError
from typing import List, Optional

import redis
import numpy as np
import re
from services.embedder import embed_and_write
from parsers.markdown_parser import markdown_parser
from parsers.web_crawler import scrape_web_docs

from typing import Literal, Union
from pydantic import BaseModel



class parser_flow(FlowSpec):
    config = Config("config", default="config.yml", parser="yaml.full_load")

    @step
    def start(self):

        # self.repo_path = "/Users/laypatel/Documents/projects/metaflow"
        # self.web_path = "https://docs.metaflow.org/"
        # self.max_iter = 30
        
        self.docs = []
        self.next(self.load_config)

    @step 
    def load_config(self):
        #TODO: Validate the source
        for src in self.config['sources']:
            if src.type == "web":
                self.web_path = src.url
                self.max_iter = src.depth
            elif src.type == "markdown":
                self.repo_path = src.path
                print(f"Parse markdown from {src.path}")
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


    

    
