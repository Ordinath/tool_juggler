from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import CallbackManager
from langchain.agents import initialize_agent, AgentType
import threading
import queue

from utils import get_secret_value

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

    def error(self, message):
        self.queue.put(f"event: error\ndata: {message}\n\n")

    def send(self, data):
        self.queue.put(data)

    def close(self):
        self.queue.put(StopIteration)


def agent_thread(app, g, last_user_message, model, tools, memory,
                 assistant_message_id):
    # print(messages)
    try:
        with app.app_context():
            agent_llm = ChatOpenAI(
                model=model,
                openai_api_key=get_secret_value('OPENAI_API_KEY'),
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
            biggy.run(input=last_user_message)
    except ValueError as e:
        if "Did not find openai_api_key" in str(e):
            g.error("No OpenAI API key provided")
        else:
            print(e)
    finally:
        g.close()
