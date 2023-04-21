from langchain.agents import Tool


def hello_world(input):
    return "Hello " + input


def get_tool(app):
    return Tool(
        name="Hello World",
        func=hello_world,
        description="useful when you need to test tools functionality. The input to this tool should be a string oh whom you want to say hello to."
    ),
