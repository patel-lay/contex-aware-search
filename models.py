from sqlalchemy import Column, Integer, String, Text
# from sqlalchemy.dialects.postgresql import VECTOR
from pgvector.sqlalchemy import Vector

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    section_id = Column(String, nullable=False)   # logical section (header, chunk group)
    source = Column(String, nullable=False)       # markdown path or web url
    chunk = Column(Text, nullable=False)          # actual text chunk
    embedding = Column(Vector(1536))              # vector embedding
