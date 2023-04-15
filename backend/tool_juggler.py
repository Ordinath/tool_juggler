from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import CallbackManager
from langchain.agents import initialize_agent, AgentType
import threading
import queue

from chain_stream_handler import ChainStreamHandler


def tool_juggler_agent(app, last_user_message, model, tools, memory, assistant_message_id):
    g = ThreadedGenerator()
    threading.Thread(target=agent_thread,
                     args=(app, g, last_user_message, model, tools, memory,
                           assistant_message_id)).start()
    return g


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


def agent_thread(app, g, last_user_message, model, tools, memory,
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
