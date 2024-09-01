import os
import uuid
from typing import List
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_postgres.vectorstores import PGVector

from chainlit.types import AskFileResponse

conninfo=os.getenv("LANGCHAIN_DB_CONNINFO")
pg_engine = create_engine(conninfo)

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
    
def index_document(file: AskFileResponse):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100
    )
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v2", 
        dashscope_api_key=os.getenv('DASHSCOPE_API_KEY')
    )
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=file.name,
        connection=conninfo,
        use_jsonb=True
    )
    if file.type == "text/plain":
        Loader = TextLoader
    elif file.type == "application/pdf":
        Loader = PyPDFLoader

    loader = Loader(file.path)
    documents = loader.load()
    chunks = text_splitter.split_documents(documents)

    if len(chunks) > 0:
        ids = []
        for i, chunk in enumerate(chunks):
            chunk.metadata['source'] = f"resource_{i}"
            ids.append(uuid.uuid1())

        vector_store.add_documents(documents=chunks, ids=ids)
    else:
        print("Embedding文件块数为0")
    


    


