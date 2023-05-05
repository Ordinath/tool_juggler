import os
import importlib
import sys
from db_models import Conversation, Message, Tool, Embedding, Secret, db
from auth import get_authenticated_user
from crypto_utils import encrypt, decrypt
from flask import current_app
import re


def create_secret(key, value):
    with current_app.app_context():
        encrypted_value = encrypt(value)
        new_secret = Secret(key=key, value=encrypted_value)
        db.session.add(new_secret)
        db.session.commit()


def get_secret_value(key):
    with current_app.app_context():
        secret = Secret.query.filter_by(key=key).first()
        if secret:
            return decrypt(secret.value)
        return None


def register_tools(app):

    with app.app_context():
        user = get_authenticated_user(app)
        tools = []
        # Fetch enabled tools from the database for the specified user
        enabled_tools = Tool.query.filter_by(enabled=True, user_id=user).all()

        print(f"Registering {len(enabled_tools)} tools")

        # Iterate through enabled tools and register them
        for tool in enabled_tools:
            # Get the tool_definition_path
            tool_definition_path = tool.tool_definition_path

            # Extract the package and module names from the path
            parent_package, module_name = os.path.split(
                tool_definition_path[:-3].replace(os.path.sep, "."))

            # Construct the module path
            module_path = f"{parent_package}.{module_name}"

            # Import the module
            spec = importlib.util.spec_from_file_location(
                module_path, tool_definition_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_path] = module
            spec.loader.exec_module(module)

            print(f"Registering tool: {module_path}")

            registered_tool = module.get_tool(app)
            tools.extend(registered_tool)

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


def normalize_string(str):
    # Replace underscores with spaces
    str = str.replace('_', ' ')

    # Remove special characters except spaces, capitalize words
    str = re.sub(r'[^a-zA-Z0-9 ]', '', str).title()

    return str


def to_snake_case(name):
    name = name.strip().lower()
    name = re.sub(r'\W+', ' ', name)  # Remove any special characters
    name = name.replace(' ', '_')
    return name


def add_core_tool(app, tool_info):
    with app.app_context():
        # Check if the core tool already exists
        core_tool = Tool.query.filter_by(name=tool_info["name"]).first()

        # If the core tool does not exist, create it
        if not core_tool:
            # Construct the dynamic path to the tool definition script
            base_path = os.path.dirname(os.path.abspath(__file__))
            tool_definition_path = os.path.join(
                base_path, tool_info["tool_definition_path"]
            )

            core_tool = Tool(
                name=tool_info["name"],
                enabled=tool_info["enabled"],
                core=tool_info["core"],
                tool_type=tool_info["tool_type"],
                tool_definition_path=tool_definition_path,
                manifest=tool_info.get("manifest"),
                description=tool_info["description"],
            )

            db.session.add(core_tool)
            db.session.commit()


def add_secret_if_not_exists(app, secret_name, secret_value):
    with app.app_context():
        # Check if the secret already exists
        secret = Secret.query.filter_by(key=secret_name).first()

        # If the secret does not exist, create it
        if not secret:
            create_secret(secret_name, secret_value)

            print(f"{secret_name} secret created with value '{secret_value}'")
        else:
            print(f"{secret_name} secret already exists")


def cut_string(string, max_len):
    if len(string) > max_len:
        return string[:max_len]
    else:
        return string
