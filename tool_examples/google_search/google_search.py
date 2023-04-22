from langchain.utilities import GoogleSearchAPIWrapper
from langchain.agents import Tool
from dotenv import load_dotenv
import os

load_dotenv()

search_tool = GoogleSearchAPIWrapper(
    google_api_key=os.environ["GOOGLE_API_KEY"],
    google_cse_id=os.environ["GOOGLE_CSE_ID"]
)


def get_tool(app):
    return Tool(
        name="Google Search",
        func=search_tool.run,
        description="useful for when you need to answer questions about current events and supply more detail about already known information. The input to this tool should be a query with a detailed explanation of what you need to know about."
    ),
