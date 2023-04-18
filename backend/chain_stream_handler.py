
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import (AgentAction, AgentFinish, LLMResult)
from typing import Any, Dict, List, Union
from urllib.parse import quote
from db_models import db, Message
import re
import json


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
        self.buffer = ""

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

                print(self.buffer)
                # Add the token to the buffer
                self.buffer += token

                # If the buffer contains a space or newline, send the buffer content to the frontend
                if " " in self.buffer or "\\n" in self.buffer:
                    # Replace newline string representation with actual newline character
                    self.buffer = self.buffer.replace("\\n", "\n")

                    encoded_buffer = quote(self.buffer)
                    self.gen.send("""data: """ + encoded_buffer.encode(
                        'latin-1', 'backslashreplace').decode('unicode-escape') +
                        """\n\n""")
                    # Clear the buffer
                    self.buffer = ""

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
