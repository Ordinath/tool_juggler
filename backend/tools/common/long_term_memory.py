from langchain.agents import Tool


def long_term_memory_tool(app, query):
    print(app.vectorstores)

    collection = app.vectorstores["long_term_memory_collection"]
    # print(collection.peek())

    number_of_embeddings = collection.count()
    # if there are no embeddings in the collection (if collection.count() returns 0), return "There is no memory" 
    if number_of_embeddings == 0:
        return "There is no memory" 

    #  if there are less then 3 embeddings in the collection, n_results should be the number of embeddings in the collection otherwise n_results should be 3
    if number_of_embeddings < 3:
        n_results = number_of_embeddings
    else:
        n_results = 3

    results = collection.query(query_texts=[query], n_results=n_results)

    print(results["documents"])
    # print(results["documents"][0][1])

    # result = ''
    # for doc in results["documents"][0]:
    #     result += doc + '\n'

    return results["documents"]


def get_tool(app):
    return Tool(
        name="Long Term Memory",
        func=lambda query: long_term_memory_tool(app, query),
        description="useful for when you need to remember things. The input to this tool should be a query with a detailed explanation of what you need to know about. It can also contain semanticaly similar words to what you are looking for and timestamps in format %Y-%m-%d."
    ),
