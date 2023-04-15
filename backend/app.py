from flask import Flask, jsonify, request, Response, stream_with_context
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import uuid
from typing import Any, Dict, List, Union
from urllib.parse import quote
import threading
import queue
import re
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import (AgentAction, AgentFinish, LLMResult)
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
import os
import importlib

from langchain.agents import initialize_agent
from langchain.agents import AgentType, AgentOutputParser

from db_models import db, Conversation, Message

load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversations.db'
db.init_app(app)
CORS(app)


class ThreadedGenerator:

    def __init__(self):
        self.queue = queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        item = self.queue.get()
        if item is StopIteration:
            raise item
        return item

    def send(self, data):
        self.queue.put(data)

    def close(self):
        self.queue.put(StopIteration)


class ChainStreamHandler(StreamingStdOutCallbackHandler):

    def __init__(self, gen, assistant_message_id):
        super().__init__()
        self.gen = gen
        self.assistant_message_id = assistant_message_id
        self.ai_message = ""
        self.start_pattern = r'"action": "Final Answer",\s+"action_input": "'
        self.end_pattern = r'"\s+}\s*```'
        self.started = False
        self.matched_start = False
        self.matched_end = False

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str],
                     **kwargs: Any) -> None:
        print("LLM Start")
        """Run when LLM starts running."""

    def on_llm_new_token(self, token: str, **kwargs):

        print(token)
        self.ai_message += token
        encoded_text = quote(token)

        if not self.started:
            if re.search(self.start_pattern, self.ai_message):
                self.started = True
                self.matched_start = True
                self.ai_message = ""
        else:
            if re.search(self.end_pattern, self.ai_message):
                self.matched_end = True
                self.ai_message = re.sub(self.end_pattern, '', self.ai_message)

            if self.matched_start and not self.matched_end:
                # self.gen.send(f"data: {encoded_text}\n\n")
                self.gen.send("""data: """ + encoded_text.encode(
                    'latin-1', 'backslashreplace').decode('unicode-escape') +
                    """\n\n""")

        # sys.stdout.write(token)
        # sys.stdout.flush()

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        print("LLM End")

        if self.started and self.ai_message and self.assistant_message_id is not None:
            # Update the message with the provided ID
            message_to_update = Message.query.get(self.assistant_message_id)
            if message_to_update:
                message_to_update.content = self.ai_message.encode(
                    'latin-1', 'backslashreplace').decode('unicode-escape')
                db.session.commit()

            encoded_done = quote("[DONE]")
            self.gen.send(f"data: {encoded_done}\n\n")

    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt],
                     **kwargs: Any) -> None:
        print("LLM Error")
        """Run when LLM errors."""

    def on_chain_start(self, serialized: Dict[str, Any],
                       inputs: Dict[str, Any], **kwargs: Any) -> None:
        print("Chain Start")
        """Run when chain starts running."""

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        print("Chain End")
        """Run when chain ends running."""

    def on_chain_error(self, error: Union[Exception, KeyboardInterrupt],
                       **kwargs: Any) -> None:
        print("Chain Error")
        """Run when chain errors."""

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str,
                      **kwargs: Any) -> None:
        print("Tool Start")
        """Run when tool starts running."""

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        print("Agent Action")
        """Run on agent action."""
        pass

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        print("Tool End")
        """Run when tool ends running."""

    def on_tool_error(self, error: Union[Exception, KeyboardInterrupt],
                      **kwargs: Any) -> None:
        print("Tool Error")
        """Run when tool errors."""

    def on_text(self, text: str, **kwargs: Any) -> None:
        print("Text")
        """Run on arbitrary text."""

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        print("Agent Finish")
        """Run on agent end."""


class CustomOutputParser(AgentOutputParser):

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={
                    "output": llm_output.split("Final Answer:")[-1].strip()
                },
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action: (.*?)[\n]*Action Input:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action,
                           tool_input=action_input.strip(" ").strip('"'),
                           log=llm_output)


def discover_tools(folders):
    tools = []

    for folder in folders:
        for filename in os.listdir(folder.replace(".", "/")):
            if not filename.endswith(".py") or filename.startswith("__"):
                continue

            module_name = filename[:-3]
            module_path = f"{folder}.{module_name}"
            module = importlib.import_module(module_path)
            tool = module.get_tool()
            tools.extend(tool)

    return tools


def agent_thread(g, last_user_message, model, tools, memory,
                 assistant_message_id):
    # print(messages)
    try:
        agent_llm = ChatOpenAI(
            model=model,
            # model='gpt-3.5-turbo',
            # model='gpt-4',
            verbose=True,
            streaming=True,
            callback_manager=CallbackManager(
                [ChainStreamHandler(g, assistant_message_id)]),
            temperature=0.7)
        biggy = initialize_agent(
            tools,
            llm=agent_llm,
            memory=memory,
            verbose=True,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        )
        with app.app_context():
            biggy.run(input=last_user_message)

    finally:
        g.close()


def biggy_agent(last_user_message, model, tools, memory, assistant_message_id):
    g = ThreadedGenerator()
    threading.Thread(target=agent_thread,
                     args=(g, last_user_message, model, tools, memory,
                           assistant_message_id)).start()
    return g


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


@app.route('/conversations/<string:conversation_id>',
           methods=['GET', 'PUT', 'DELETE'])
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


@app.route('/conversations/<string:conversation_id>/messages',
           methods=['POST'])
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


@app.route('/conversations/<string:conversation_id>/getAICompletion',
           methods=['POST'])
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

    print('tools', tools)

    return Response(
        stream_with_context(
            biggy_agent(last_user_message, model, tools, memory,
                        assistant_message_id)),
        content_type="text/event-stream")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5005)
