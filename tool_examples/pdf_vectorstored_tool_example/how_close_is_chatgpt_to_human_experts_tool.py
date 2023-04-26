from langchain.agents import Tool


def how_close_is_chatgpt_to_human_experts_tool(app, query):

    collection = app.vectorstores["how_close_is_chatgpt_to_human_experts"]["collection"]
    print('how_close_is_chatgpt_to_human_experts collection contains ',
          collection.count())

    number_of_embeddings = collection.count()
    if number_of_embeddings == 0:
        return "There is no memory"

    if number_of_embeddings < 3:
        n_results = number_of_embeddings
    else:
        n_results = 3

    results = collection.query(query_texts=[query], n_results=n_results)

    return results["documents"]


def get_tool(app):
    return Tool(
        name="How close is ChatGPT to Human Experts",
        func=lambda query: how_close_is_chatgpt_to_human_experts_tool(
            app, query),
        description="useful for when you need to anwser questions and get to know more about How close is ChatGPT to Human Experts. The input to this tool should be a query with a detailed explanation of what you need to know about. It can also contain semantically similar words to what you are looking."
    ),
