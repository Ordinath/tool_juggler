from langchain.agents import Tool


def ${pdf_snake_case_name}_tool(app, query):

    collection = app.vectorstores["${pdf_snake_case_name}"]["collection"]
    # print(collection.peek())
    print('${pdf_snake_case_name} collection contains ',
          collection.count())

    number_of_embeddings = collection.count()
    # if there are no embeddings in the collection (if collection.count() returns 0), return "There is no memory"
    if number_of_embeddings == 0:
        return "There is no memory"

    #  if there are less then 5 embeddings in the collection, n_results should be the number of embeddings in the collection otherwise n_results should be 5
    if number_of_embeddings < 5:
        n_results = number_of_embeddings
    else:
        n_results = 5

    results = collection.query(query_texts=[query], n_results=n_results)

    return results["documents"]


def get_tool(app):
    return Tool(
        name="${pdf_tool_name}",
        func=lambda query: ${pdf_snake_case_name}_tool(
            app, query),
        description="useful for when you need to anwser questions and get to know more about ${pdf_tool_name}. The input to this tool should be a query with a detailed explanation of what you need to know about. It can also contain semantically similar words to what you are looking."
    ),