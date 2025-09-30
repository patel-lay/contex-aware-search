# crud/document.py
from models import Document
from db import get_session

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy import select

load_dotenv()

def add_document(doc):
    with get_session() as session:
        data_to_write = Document(
            section_id = doc["section_id"],
            source = doc["path"],
            chunk = doc["content"],
            embedding = doc["embedding"]
        )
        session.add(data_to_write)


sql = text("""
    SELECT id, section_id, source, chunk, embedding <=> :query_embedding AS distance
    FROM documents
    ORDER BY distance
    LIMIT 3;
""")
sql2 = text("""SELECT id, section_id, source, chunk, embedding
    FROM documents
    ORDER BY embedding <=> :query_embedding::vector
    LIMIT 5;
""")

def retrive_document(query_embedding, top_k: int = 3):
    print(type(query_embedding), len(query_embedding))
    # print("curr", query_embedding)
    with get_session() as session:
        # results = (
        # session.query(
        #     Document,
        #     (Document.embedding.op("<=>")(query_embedding)).label("distance")
        # )
        # .order_by("distance")
        # .limit(5)
        # .all()
        # )
        query = (
        select(Document)
        .order_by(Document.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        )
        results = session.execute(query).scalars().all()
        for obj in results:
            session.expunge(obj)

    return results
