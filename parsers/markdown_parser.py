#Read the document and parse it make it ready for indexing. 
import os 
from parsers.common_parser import prepare_chunks_markdown  

def markdown_parser(doc, repo_path):
    # docs = []
    for path, _ , files in os.walk(repo_path):
        for f in files:
            if f.endswith((".md")):
                with open(os.path.join(path, f), "r", encoding="utf-8") as fh:
                    full_path = os.path.join(path, f)
                    prepare_chunks_markdown(doc, fh.read(), full_path)
    return doc

