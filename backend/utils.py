import os
import importlib
from db_models import Conversation, Message, Embedding, db


def discover_tools(folders, app):
    tools = []

    for folder in folders:
        for filename in os.listdir(folder.replace(".", "/")):
            if not filename.endswith(".py") or filename.startswith("__"):
                continue

            module_name = filename[:-3]
            module_path = f"{folder}.{module_name}"
            module = importlib.import_module(module_path)
            tool = module.get_tool(app)
            tools.extend(tool)

    return tools


def upsert_embeddings(app, conversation_id, vectorstore, embedding_strings):
    new_embeddings = []

    with app.app_context():
        # Get the conversation by ID
        conversation = Conversation.query.get_or_404(conversation_id)
        conversation.embedded = True
        db.session.commit()

        # Check if the conversation has any embeddings
        if conversation.embeddings:

            existing_embedding_ids = [
                embedding.id for embedding in conversation.embeddings]

            # Delete existing embeddings from vectorstore

            vectorstore['collection'].delete(ids=existing_embedding_ids)
            vectorstore['client'].persist()

            # Delete existing embeddings from SQLite database
            Embedding.query.filter_by(conversation_id=conversation_id).delete()
            db.session.commit()

        # Create new embeddings and add them to the SQLite database
        for content in embedding_strings:
            new_embedding = Embedding(conversation_id=conversation_id)
            db.session.add(new_embedding)
            db.session.commit()
            new_embeddings.append({"id": new_embedding.id, "content": content})

        # Add new embeddings to vectorstore
        documents = [item['content'] for item in new_embeddings]
        ids = [item['id'] for item in new_embeddings]
        print('before emb upsert', vectorstore['collection'].count())
        vectorstore['collection'].add(documents=documents, ids=ids)
        print('after emb upsert', vectorstore['collection'].count())
        vectorstore['client'].persist()

    return new_embeddings
