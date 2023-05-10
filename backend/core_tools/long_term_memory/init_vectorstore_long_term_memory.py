import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from utils import get_vectorstore_persist_directory

def init_vectorstore_long_term_memory(app):
    persist_directory = get_vectorstore_persist_directory(
        app, 'private', 'long_term_memory')

    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        # Optional, defaults to .chromadb/ in the current directory
        persist_directory=persist_directory
    ))
    client.persist()
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2")
    collection = client.get_or_create_collection(
        name="long_term_memory", embedding_function=sentence_transformer_ef)

    print('long_term_memory collection initialized with number of embeddings: ',
          collection.count())

    return {"client": client, "collection": collection}


