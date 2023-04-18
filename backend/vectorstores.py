import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import inspect
import sys


def init_vector_store_long_term_memory():
    persist_directory = 'data/common/vectorstores/long_term_memory_chroma'
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


# def init_vector_store_2():
#     # Initialize and return the second VectorStore client
#     pass


def register_vectorstores(app):
    vectorstores = {}

    # Iterate over all functions defined in this module
    for name, function in inspect.getmembers(sys.modules[__name__], inspect.isfunction):
        # If the function name starts with 'init_vector_store_', call the function and store the result
        if name.startswith('init_vector_store_'):
            vectorstore_name = name.replace('init_vector_store_', '')
            vectorstores[vectorstore_name] = function()

    app.vectorstores = vectorstores
