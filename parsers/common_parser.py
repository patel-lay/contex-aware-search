import re 

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

def prepare_chunks(docs, markdown_text, path):
    for i, sec in enumerate(markdown_text):
        sec_chunks = chunk_text(sec["content"])
        for j, chunk in enumerate(sec_chunks):
            docs.append({
                "repo": "metaflow/web_doc",
                "path": path + "Section:" +  sec["title"],
                "section_id": i,
                "chunk_id": j,
                "content": chunk
            })

def prepare_chunks_markdown(docs, markdown_text, path):
    sections = split_markdown_sections(markdown_text)
    for i, sec in enumerate(sections):
        sec_chunks = chunk_text(sec)
        for j, chunk in enumerate(sec_chunks):
            docs.append({
                "repo": "metaflow/markdown",
                "path": path,
                "section_id": i,
                "chunk_id": j,
                "content": chunk
            })


def split_markdown_sections(text: str):
    sections = re.split(r"\n(?=#)", text)  # split on headers starting with "#"
    return [s.strip() for s in sections if s.strip()]
