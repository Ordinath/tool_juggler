import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
# get_secret_value is the function to be used within all tool components to get secrets
from utils import get_secret_value


def init_vectorstore_how_close_is_chatgpt_to_human_experts(app):
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    persist_directory = os.path.join(
        current_file_path, '..', 'vectorstores', 'how_close_is_chatgpt_to_human_experts')

    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        # Optional, defaults to .chromadb/ in the current directory
        persist_directory=persist_directory
    ))
    client.persist()
    embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        model_name="text-embedding-ada-002", api_key=get_secret_value("OPENAI_API_KEY"))
    collection = client.get_or_create_collection(
        name="how_close_is_chatgpt_to_human_experts", embedding_function=embedding_function)

    print('how_close_is_chatgpt_to_human_experts collection initialized with number of embeddings: ',
          collection.count())

    return {"client": client, "collection": collection}
