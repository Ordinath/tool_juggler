from flask import jsonify, request, Response, stream_with_context
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from db_models import Conversation, Message, db
from utils import discover_tools
from tool_juggler import tool_juggler_agent


def register_routes(app):
    @app.route('/conversations', methods=['GET', 'POST'])
    def conversations():
        if request.method == 'POST':
            data = request.json
            new_conversation = Conversation(title=data['title'],
                                            model=data.get('model'))
            db.session.add(new_conversation)
            db.session.commit()
            return jsonify({
                "id": new_conversation.id,
                "title": new_conversation.title
            }), 201

        conversations = Conversation.query.all()
        return jsonify([{
            "id": conv.id,
            "title": conv.title
        } for conv in conversations])

    @app.route('/conversations/<string:conversation_id>', methods=['GET', 'PUT', 'DELETE'])
    def conversation(conversation_id):
        conv = Conversation.query.get_or_404(conversation_id)

        if request.method == 'PUT':
            data = request.json
            conv.title = data['title']
            db.session.commit()

        elif request.method == 'DELETE':
            # Delete messages associated with the conversation
            for msg in conv.messages:
                db.session.delete(msg)

            db.session.delete(conv)
            db.session.commit()
            return '', 204

        messages = [{
            "id": msg.id,
            "sender": msg.sender,
            "content": msg.content,
            "timestamp": msg.timestamp
        } for msg in conv.messages]
        return jsonify({"id": conv.id, "title": conv.title, "messages": messages})

    @app.route('/conversations/<string:conversation_id>/messages', methods=['POST'])
    def add_message(conversation_id):
        conv = Conversation.query.get_or_404(conversation_id)
        data = request.json
        new_message = Message(sender=data['sender'],
                              content=data['content'],
                              timestamp=data['timestamp'],
                              conversation_id=conv.id)
        db.session.add(new_message)
        db.session.commit()
        return jsonify({"id": new_message.id}), 201

    @app.route('/messages/<string:message_id>', methods=['PUT', 'DELETE'])
    def message(message_id):
        msg = Message.query.get_or_404(message_id)

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
    def get_ai_completion(conversation_id):
        data = request.json
        assistant_message_id = data.get('assistant_message_id', None)
        model = data.get('model', None)
        conv = Conversation.query.get_or_404(conversation_id)
        print('conv', conv)
        print('conv.messages', conv.messages)
        for msg in conv.messages:
            print('msg', msg.sender, msg.content)
        # extract last user message to a variable and remove it from the conversation
        # conv.messages.sort(key=lambda x: x.timestamp)
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

        print('last_user_message', last_user_message)
        print('message_history', message_history)


        memory = ConversationBufferMemory(memory_key="chat_history",
                                        return_messages=True,
                                        chat_memory=message_history)
        
        folders = ["tools.common", "tools.private"]
        tools = discover_tools(folders)

        return Response(
            stream_with_context(
                tool_juggler_agent(app, last_user_message, model, tools, memory,
                            assistant_message_id)),
            content_type="text/event-stream")
    
    # @app.route('/conversations/<string:conversation_id>/upsert_embedding', methods=['POST'])
    # def upsert_embedding(conversation_id):
    #     persist_directory = "data/common/vectorstores/long_term_memory_chroma"
    #     client = chromadb.Client(Settings(
    #         chroma_db_impl="duckdb+parquet",
    #         # Optional, defaults to .chromadb/ in the current directory
    #         persist_directory=persist_directory
    #     ))
    #     sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    #         model_name="all-MiniLM-L6-v2")

    #     collection = client.get_or_create_collection(
    #         name="long_term_memory_collection", embedding_function=sentence_transformer_ef)
        
    #     # if embedding already exists, update it
    #     collection.get(ids=[conversation_id])
