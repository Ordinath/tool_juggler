import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from utils import get_secret_value


def init_vectorstore_${pdf_snake_case_name}(app):
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    persist_directory = os.path.join(
        current_file_path, '..', 'vectorstores', '${pdf_snake_case_name}')

    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=persist_directory
    ))
    client.persist()
    embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        model_name="text-embedding-ada-002", api_key=get_secret_value("OPENAI_API_KEY"))
    collection = client.get_or_create_collection(
        name="${pdf_snake_case_name_max_63_char}", embedding_function=embedding_function)

    print('${pdf_snake_case_name} collection initialized with number of embeddings: ',
          collection.count())

    return {"client": client, "collection": collection}
