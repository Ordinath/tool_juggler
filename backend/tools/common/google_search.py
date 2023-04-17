from langchain.utilities import GoogleSearchAPIWrapper
from langchain.agents import Tool

search_tool = GoogleSearchAPIWrapper()


def get_tool(app):
    return Tool(
        name="Search",
        func=search_tool.run,
        description="useful for when you need to answer questions about current events and supply more detail about already known information. The input to this tool should be a query with a detailed explanation of what you need to know about."
    ),
