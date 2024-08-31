import os
from typing import List
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

pg_engine = create_engine(
    os.getenv("LANGCHAIN_DB_CONNINFO")
)

class PG_COLLECTION(declarative_base()):
    __tablename__ = 'langchain_pg_collection'
    uuid = Column(String, primary_key=True)
    name = Column(String, unique = True)
    cmetadata = Column(String)

def get_collections() -> List[str]:
    Session = sessionmaker(bind=pg_engine)
    with Session() as session:
        collections = session.query(PG_COLLECTION).all()
        session.close()
        return [collection.name for collection in collections]
