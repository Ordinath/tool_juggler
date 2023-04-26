from langchain.document_loaders import PyPDFLoader
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os
# get_secret_value is the function to be used within all tool components to get secrets
from utils import get_secret_value


def prepare_how_close_is_chatgpt_to_human_experts(app):
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    persist_directory = os.path.join(
        current_file_path, '..', '..', 'vectorstores', 'how_close_is_chatgpt_to_human_experts')

    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=persist_directory
    ))

    embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        model_name="text-embedding-ada-002", api_key=get_secret_value("OPENAI_API_KEY"))

    collection = client.get_or_create_collection(
        name="how_close_is_chatgpt_to_human_experts", embedding_function=embedding_function)

    # only add the documents if the collection is empty
    if collection.count() < 1:
        # Calculate the absolute path of the PDF file
        pdf_path = os.path.join(
            current_file_path, "How_Close_is_ChatGPT_to_Human_Experts.pdf")
        loader = PyPDFLoader(pdf_path)
        pages = loader.load_and_split()
        # print(pages[0])

        # create an array of page_contents from the pages
        documents = [page.page_content for page in pages]
        ids = [str(i) for i in range(1, len(pages) + 1)]

        # add the documents to the collection
        collection.add(
            documents=documents,
            ids=ids
        )

        client.persist()
