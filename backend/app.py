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
from langchain.schema import (HumanMessage, AIMessage, SystemMessage,
                              AgentAction, AgentFinish, LLMResult)
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor, ConversationalChatAgent
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.vectorstores import Chroma
from langchain.utilities import GoogleSearchAPIWrapper
from requests_oauthlib import OAuth1Session
import os

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from langchain.agents import initialize_agent
from langchain.agents import AgentType, AgentOutputParser

load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversations.db'
db = SQLAlchemy(app)
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

    # def __init__(self, gen, assistant_message_id):
    #     super().__init__()
    #     self.gen = gen
    #     self.assistant_message_id = assistant_message_id
    #     self.ai_message = ""

    # def on_llm_new_token(self, token: str, **kwargs):
    #     # print("LLM New Token")
    #     self.ai_message += token
    #     encoded_text = quote(token)
    #     self.gen.send(f"data: {encoded_text}\n\n")

    # def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
    #     # print("LLM End")
    #     if self.ai_message and self.assistant_message_id is not None:
    #         # Update the message with the provided ID
    #         message_to_update = Message.query.get(self.assistant_message_id)
    #         if message_to_update:
    #             message_to_update.content = self.ai_message
    #             db.session.commit()

    #     encoded_done = quote("[DONE]")
    #     self.gen.send(f"data: {encoded_done}\n\n")

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


# def llm_thread(g, messages, assistant_message_id, model):
#     print(messages)
#     try:
#         chat = ChatOpenAI(
#             model=model,
#             verbose=True,
#             streaming=True,
#             callback_manager=CallbackManager(
#                 [ChainStreamHandler(g, assistant_message_id)]),
#             temperature=0.7,
#         )
#         with app.app_context():
#             chat(messages)


#     finally:
#         g.close()
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
            # agent_kwargs={"output_parser": CustomOutputParser()}
            # callback_manager=CallbackManager(
            #     [ChainStreamHandler(g, assistant_message_id)]),
        )
        # biggy = AgentExecutor.from_agent_and_tools(
        #     agent=agent,
        #     tools=tools,
        #     verbose=True,
        #     # callback_manager=CallbackManager(
        #     #     [ChainStreamHandler(g, assistant_message_id)]),
        #     memory=memory)
        # chat = ChatOpenAI(
        #     model=model,
        #     verbose=True,
        #     streaming=True,
        #     callback_manager=CallbackManager(
        #         [ChainStreamHandler(g, assistant_message_id)]),
        #     temperature=0.7,
        # )
        with app.app_context():
            biggy.run(input=last_user_message)

    finally:
        g.close()


# def chat(messages, assistant_message_id, model):
#     g = ThreadedGenerator()
#     threading.Thread(target=llm_thread,
#                      args=(g, messages, assistant_message_id, model)).start()
#     return g


def biggy_agent(last_user_message, model, tools, memory, assistant_message_id):
    g = ThreadedGenerator()
    threading.Thread(target=agent_thread,
                     args=(g, last_user_message, model, tools, memory,
                           assistant_message_id)).start()
    return g


class Conversation(db.Model):
    id = db.Column(db.String(36),
                   primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(50), nullable=True)
    messages = db.relationship('Message', backref='conversation', lazy=True)


class Message(db.Model):
    id = db.Column(db.String(36),
                   primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    sender = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.String(255), nullable=False)
    conversation_id = db.Column(db.String(36),
                                db.ForeignKey('conversation.id'),
                                nullable=False)


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

    # template = """
    # You are a helpful assistant. You are especially strong in Programming.
    # You always consider user's request critically and try to find the best possible solution,
    # even if you need to completely overhaul the existing solution to make it better.
    # You always follow modern development practices and try to follow best programming principles like 
    # KISS, DRY, YAGNI, Composition Over Inheritance, Single Responsibility, Separation of Concerns, SOLID.
    # {input}
    # CODE ONLY
    # """

    # prompt = PromptTemplate(input_variables=["input", "chat_history"], template=template)
    # prompt = PromptTemplate(input_variables=["input"], template=template)

    # llm = ChatOpenAI(
    #     # model='gpt-3.5-turbo',
    #     model='gpt-4',
    #     verbose=True,
    #     # streaming=True,
    #     # callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    #     temperature=0.7)

    # programming_tool = LLMChain(
    #     llm=llm,
    #     prompt=prompt,
    #     verbose=True,
    #     # memory=readonlymemory,
    # )

    # search tool
    search_tool = GoogleSearchAPIWrapper()
    
    # tools
    tools = [
        Tool(
            name="Search",
            func=search_tool.run,
            description=
            "useful for when you need to answer questions about current events and supply more detail about already known information. The input to this tool should be a query with a detailed explanation of what you need to know about."
        )
    ]

    # # biggy agent
    # prefix = """Your name is Biggy! Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
    # suffix = """
    # Use the following format:

    # Question: the input question you must answer
    # Thought: you should always think about what to do
    # Action: the action to take, should be one of tool names
    # Action Input: the input to the action
    # Observation: the result of the action
    # ... (this Thought/Action/Action Input/Observation can repeat N times)
    # Thought: I now know the final answer
    # Final Answer: the final answer to the original input question
    # Begin!"

    # {chat_history}
    # Question: {input}
    # {agent_scratchpad}"""

    # prompt = ConversationalChatAgent.create_prompt(
    #     tools,
    #     # system_message=prefix,
    #     # human_message=suffix,
    #     input_variables=["input", "chat_history", "agent_scratchpad"])

    # llm_chain = LLMChain(

    # prompt=prompt)

    # agent_chain = initialize_agent()

    # agent = ConversationalChatAgent(llm_chain=llm_chain, tools=tools, verbose=True)

    return Response(
        stream_with_context(
            # chat(messages, assistant_message_id, model)),
            biggy_agent(last_user_message, model, tools, memory,
                        assistant_message_id)),
        content_type="text/event-stream")
    # stream_with_context(
    #     # chat(messages, assistant_message_id, model)),
    #     biggy_agent(last_user_message, agent, tools, memory,
    #                 assistant_message_id)),
    # content_type="text/event-stream")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5005)
