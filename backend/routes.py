from flask import jsonify, request, Response, stream_with_context
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from datetime import datetime, timedelta
from sqlalchemy import exc
import chromadb
import jwt
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from db_models import User, Conversation, Message, Embedding, Tool, Secret, db
from utils import register_tools, upsert_embeddings
from auth import get_authenticated_user, require_auth
from tool_juggler import tool_juggler_agent
from tool_processor import ToolProcessor, remove_tool_files, initialize_core_tools
import os
from werkzeug.utils import secure_filename
from functools import wraps
from werkzeug.exceptions import HTTPException
from crypto_utils import encrypt, decrypt
from functools import wraps
from vectorstores import register_vectorstores
# from utils import add_core_tool, add_secret_if_not_exists
# from core_tools import long_term_memory_tool
# app.config['UPLOAD_FOLDER'] = 'path/to/your/upload/directory'


def register_routes(app):
    @app.route('/conversations', methods=['GET', 'POST'])
    @require_auth
    def conversations():
        user = get_authenticated_user(app)
        if request.method == 'POST':
            data = request.json
            new_conversation = Conversation(title=data['title'],
                                            model=data.get('model'),
                                            user_id=user.id)
            db.session.add(new_conversation)
            db.session.commit()
            return jsonify({
                "id": new_conversation.id,
                "title": new_conversation.title
            }), 201

        conversations = Conversation.query.filter_by(user_id=user.id).all()
        return jsonify([{
            "id": conv.id,
            "title": conv.title,
            "embedded": conv.embedded,
        } for conv in conversations])

    @app.route('/conversations/<string:conversation_id>', methods=['GET', 'PUT', 'DELETE'])
    @require_auth
    def conversation(conversation_id):
        user = get_authenticated_user(app)
        conv = Conversation.query.get_or_404(conversation_id)

        if conv.user_id != user.id:
            return jsonify({"error": "Unauthorized access to the conversation."}), 403

        if request.method == 'PUT':
            data = request.json
            conv.title = data['title']
            db.session.commit()

        elif request.method == 'DELETE':
            # Delete messages associated with the conversation
            for msg in conv.messages:
                db.session.delete(msg)

            # Delete embeddings associated with the conversation
            embedding_ids_to_delete = []
            for emb in conv.embeddings:
                embedding_ids_to_delete.append(emb.id)
                db.session.delete(emb)

            # potential todo re setup embedding deletion to a user based deletion
            # Remove embeddings from the vector-based data store if there are any
            if embedding_ids_to_delete:
                client = app.vectorstores['long_term_memory']['client']
                collection = app.vectorstores['long_term_memory']['collection']
                collection.delete(ids=embedding_ids_to_delete)
                client.persist()

            db.session.delete(conv)
            db.session.commit()
            return '', 204

        messages = [{
            "id": msg.id,
            "sender": msg.sender,
            "content": msg.content,
            "timestamp": msg.timestamp
        } for msg in conv.messages]

        return jsonify({
            "id": conv.id,
            "title": conv.title,
            "embedded": conv.embedded,
            "messages": messages
        })

    @app.route('/conversations/<string:conversation_id>/messages', methods=['POST'])
    @require_auth
    def add_message(conversation_id):
        user = get_authenticated_user(app)
        conv = Conversation.query.get_or_404(conversation_id)

        if conv.user_id != user.id:
            return jsonify({"error": "Unauthorized access to the conversation."}), 403

        data = request.json
        new_message = Message(sender=data['sender'],
                              content=data['content'],
                              timestamp=data['timestamp'],
                              conversation_id=conv.id)
        db.session.add(new_message)
        db.session.commit()
        return jsonify({"id": new_message.id}), 201

    @app.route('/messages/<string:message_id>', methods=['PUT', 'DELETE'])
    @require_auth
    def message(message_id):
        user = get_authenticated_user(app)
        msg = Message.query.get_or_404(message_id)
        conv = Conversation.query.get_or_404(msg.conversation_id)

        if conv.user_id != user.id:
            return jsonify({"error": "Unauthorized access to the conversation."}), 403

        if request.method == 'PUT':
            data = request.json
            msg.content = data['content']
            db.session.commit()

        elif request.method == 'DELETE':
            db.session.delete(msg)
            db.session.commit()
            return '', 204

        return jsonify({
            "id": msg.id,
            "sender": msg.sender,
            "content": msg.content,
            "timestamp": msg.timestamp
        })

    @app.route('/conversations/<string:conversation_id>/get_ai_completion', methods=['POST'])
    @require_auth
    def get_ai_completion(conversation_id):

        user = get_authenticated_user(app)
        data = request.json
        assistant_message_id = data.get('assistant_message_id', None)

        model = data.get('model', None)
        conv = Conversation.query.get_or_404(conversation_id)

        if conv.user_id != user.id:
            return jsonify({"error": "Unauthorized access to the conversation."}), 403

        last_assistant_message = conv.messages[-1].content
        conv.messages = conv.messages[:-1]
        last_user_message = conv.messages[-1].content
        conv.messages = conv.messages[:-1]

        message_history = ChatMessageHistory()
        # messages = []
        for msg in conv.messages:
            if msg.sender == "user":
                message_history.add_user_message(message=msg.content)
            elif msg.sender == "assistant":
                message_history.add_ai_message(message=msg.content)

        # print('last_user_message', last_user_message)
        # print('message_history', message_history)

        memory = ConversationBufferMemory(memory_key="chat_history",
                                          return_messages=True,
                                          chat_memory=message_history)

        tools = register_tools(app)

        return Response(
            stream_with_context(
                tool_juggler_agent(app, last_user_message, model, tools, memory,
                                   assistant_message_id)),
            content_type="text/event-stream")

    @app.route('/conversations/<string:conversation_id>/upsert_long_term_memory_embedding', methods=['POST'])
    @require_auth
    def upsert_long_term_memory_embedding(conversation_id):
        user = get_authenticated_user(app)
        conv = Conversation.query.get_or_404(conversation_id)

        if conv.user_id != user.id:
            return jsonify({"error": "Unauthorized access to the conversation."}), 403

        messages_to_embed = ""
        for msg in conv.messages:

            timestamp = datetime.fromisoformat(msg.timestamp.replace("Z", ""))
            formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M")

            new_msg = """\n{timestamp} - {sender}: {content}"""
            messages_to_embed += new_msg.format(
                timestamp=formatted_timestamp, sender=msg.sender, content=msg.content)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=0)
        messages_to_embed_chunks = text_splitter.split_text(messages_to_embed)

        upsert_embeddings(app, conversation_id, app.vectorstores['long_term_memory'],
                          messages_to_embed_chunks)

        return jsonify({"id": conversation_id}), 201

    @app.route('/conversations/<string:conversation_id>/delete_long_term_memory_embedding', methods=['DELETE'])
    @require_auth
    def delete_long_term_memory_embedding(conversation_id):
        user = get_authenticated_user(app)
        conv = Conversation.query.get_or_404(conversation_id)

        if conv.user_id != user.id:
            return jsonify({"error": "Unauthorized access to the conversation."}), 403

        # Set the embedded flag to False for the conversation
        conv.embedded = False
        embedding_ids_to_delete = []
        for emb in conv.embeddings:
            embedding_ids_to_delete.append(emb.id)
            db.session.delete(emb)

        # Remove embeddings from the vector-based data store
        client = app.vectorstores['long_term_memory']['client']
        collection = app.vectorstores['long_term_memory']['collection']
        print('before emb delete', collection.count())
        collection.delete(ids=embedding_ids_to_delete)
        print('after emb delete', collection.count())
        client.persist()

        db.session.commit()

        return '', 204

    @app.route('/upload_tool_zip', methods=['POST'])
    @require_auth
    def upload_tool_zip():
        user = get_authenticated_user(app)
        # print(request.files)
        if 'upload_file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['upload_file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(file.filename)
            file_path = os.path.join('resources', 'tool_packages', filename)
            dir_path = os.path.dirname(file_path)
            os.makedirs(dir_path, exist_ok=True)
            file.save(file_path)

            tool_processor = ToolProcessor(app, file_path)
            processing_result = tool_processor.process_file()

            return jsonify({'message': processing_result}), 200 if processing_result == "Tool processed successfully" else 400

    @app.route('/tools', methods=['GET'])
    @require_auth
    def get_tools():
        user = get_authenticated_user(app)
        tools = Tool.query.filter_by(user_id=user.id).all()
        return jsonify([{
            "id": tool.id,
            "name": tool.name,
            "enabled": tool.enabled,
            "core": tool.core,
            "tool_type": tool.tool_type,
            "manifest": tool.manifest,
            "description": tool.description,
            "created_at": tool.created_at.isoformat(),
            "updated_at": tool.updated_at.isoformat() if tool.updated_at else None,
        } for tool in tools])

    @app.route('/tools/<string:tool_id>/toggle', methods=['PUT'])
    @require_auth
    def toggle_tool(tool_id):
        user = get_authenticated_user(app)
        tool = Tool.query.get_or_404(tool_id)

        if tool.user_id != user.id:
            return jsonify({"error": "Unauthorized access to the tool."}), 403

        data = request.json
        enabled = data['enabled']

        # print('tool_id', tool_id)
        # print('enabled', data['enabled'])
        try:
            tool = Tool.query.get_or_404(tool_id)
            tool.enabled = enabled
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(str(e))
            return jsonify({"error": "An error occurred while toggling the tool."}), 500

        return '', 204

    @app.route('/tools/<string:tool_id>', methods=['DELETE'])
    @require_auth
    def delete_tool(tool_id):
        user = get_authenticated_user(app)
        tool = Tool.query.get_or_404(tool_id)

        if tool.user_id != user.id:
            return jsonify({"error": "Unauthorized access to the tool."}), 403

        try:
            tool = Tool.query.get_or_404(tool_id)

            # Remove tool files from the file system
            remove_tool_files(tool)

            db.session.delete(tool)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(str(e))
            return jsonify({"error": "An error occurred while deleting the tool."}), 500

        return '', 204

    @app.route('/secrets', methods=['GET', 'POST'])
    @require_auth
    def secrets():
        user = get_authenticated_user(app)
        if request.method == 'POST':
            data = request.json
            encrypted_value = encrypt(data['value'])
            new_secret = Secret(
                key=data['key'], value=encrypted_value, user_id=user.id)
            db.session.add(new_secret)
            db.session.commit()
            return jsonify({"id": new_secret.id, "key": new_secret.key}), 201

        secrets = Secret.query.filter_by(user_id=user.id).all()
        return jsonify([{"id": secret.id, "key": secret.key, "value": decrypt(secret.value)} for secret in secrets])

    @app.route('/secrets/<string:secret_id>', methods=['GET', 'PUT', 'DELETE'])
    @require_auth
    def secret(secret_id):
        user = get_authenticated_user(app)
        secret = Secret.query.get_or_404(secret_id)

        if secret.user_id != user.id:
            return jsonify({"error": "Unauthorized access to the secret."}), 403

        if request.method == 'GET':
            decrypted_value = decrypt(secret.value)
            return jsonify({"id": secret.id, "key": secret.key, "value": decrypted_value})

        if request.method == 'PUT':
            data = request.json
            secret.key = data['key']
            secret.value = encrypt(data['value'])
            db.session.commit()
            return jsonify({"id": secret.id, "key": secret.key, "value": data['value']})

        if request.method == 'DELETE':
            db.session.delete(secret)
            db.session.commit()
            return '', 204

    @app.route('/register', methods=['POST'])
    def register():
        data = request.json
        email = data['email']
        password = data['password']

        # Check if the email is already taken
        if User.query.filter_by(email=email).first() is not None:
            return jsonify({"error": "Email already registered"}), 400

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        initialize_core_tools(app)

        return jsonify({"message": "User registered successfully"}), 201

    @app.route('/login', methods=['POST'])
    def login():
        data = request.json
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            return jsonify({"error": "Invalid email or password"}), 401

        token = jwt.encode(
            {"user_id": user.id, "exp": datetime.utcnow() + timedelta(hours=24)},
            app.config['JWT_SECRET_KEY'],
            algorithm="HS256",
        )

        app.current_user_id = user.id

        # we initiate the app for logged in user
        register_vectorstores(app)
        print(app.vectorstores)
        # add_core_tool(app, long_term_memory_tool)
        # add_secret_if_not_exists(app, "OPENAI_API_KEY", "TO_BE_PROVIDED")

        return jsonify({"token": token})

    @app.errorhandler(Exception)
    def handle_exception(e):
        # handle OpenAI API key not found error
        if isinstance(e, ValueError) and "Did not find openai_api_key" in str(e):
            return {"error": "OpenAI API key not found."}, 400
        # handle other exceptions
        if isinstance(e, HTTPException):
            return e.get_response()
        return {"error": str(e)}, 500


def allowed_extension(extension):
    ALLOWED_EXTENSIONS = {'zip', 'pdf'}
    return extension in ALLOWED_EXTENSIONS


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'zip', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
