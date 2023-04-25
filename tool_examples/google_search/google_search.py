from langchain.utilities import GoogleSearchAPIWrapper
from langchain.agents import Tool
# get_secret_value is the function to be used within all tool components to get secrets
from utils import get_secret_value

search_tool = GoogleSearchAPIWrapper(
    google_api_key=get_secret_value("GOOGLE_API_KEY"),
    google_cse_id=get_secret_value("GOOGLE_CSE_ID")
)


def get_tool(app):
    return Tool(
        name="Google Search",
        func=search_tool.run,
        description="useful for when you need to answer questions about current events and supply more detail about already known information. The input to this tool should be a query with a detailed explanation of what you need to know about."
    ),
