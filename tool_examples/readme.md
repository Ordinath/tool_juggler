# Tool Juggler - Tool Uploading Documentation

This document explains the process and requirements for uploading a new tool to the Tool Juggler platform. The folder contains examples of tools that can be uploaded to the platform. To test the functionality, archive these folders into a zip file and upload them using the Tool Juggler frontend drag-and-drop box.

## Manifest File Structure

The `manifest.json` file is a key component of the tool uploading process, as it provides necessary information about the tool. The following is an example of a basic `manifest.json` template:

**Note:** The `name`, `tool_type`, and `tool_definition` fields in the manifest file are always required. Make sure to provide these fields when creating a new tool.

```json
{
    "name": "example", // required
    "version": "0.1",
    "tool_type": "common", // or "private" - required
    "tool_definition": "example.py", // required
    "requirements": "example_requirements.txt",
    "vectorstore_init": null, // or *.py
    "prep_script": "example_prep.py", // or null
    "env_vars": [
        "EXAMPLE_VAR",
        "EXAMPLE_VAR_2"
    ]
}
```

### Required Fields

- `name`: The name of the tool. This will be used in various ways within the tool processing, such as generating a unique identifier for the tool. This value will be camel cased and used as a name for vector store init scripts, for example.
- `tool_type`: Determines if the tool is "common" or "private". Common tools go into a shared folder, while private tools are owned by a specific user and stored in a private folder. All contents of the private folder will be git-ignored.
- `tool_definition`: Specifies the script that represents the tool itself. This script must always contain a `get_tool` function that returns a `langchain.agent.Tool` class instance, as shown in the example below.

### Optional Fields

- `version`: A simple version representation for the tool. This value is used for reference purposes only and does not affect tool processing logic.
- `requirements`: A text file listing any Python packages required to run the prep script or vector store init script. These dependencies will be installed via pip in the application backend's virtual environment.
- `vectorstore_init`: A script that initializes a vector store if required by the tool. If the tool relies on a vector store during execution, this script must be provided and properly formatted. Check the `pdf_vectorstored_tool_example` for an example of this script.
- `prep_script`: A script that runs after installing the requirements but before initializing the vector store. This script might load a PDF or CSV file, for example, and create a vector store. The `pdf_vectorstored_tool_example` also contains an example of a prep script. The main entry point of such script must follow the naming convention of `prepare_{name of the tool}`.
- `env_vars`: An array of environment variables required by the tool. if there is a .env file provided in the tool archive folder, the values in that file will be used to populate the environment variables, that are listed in the manifest. Otherwise, the variables provided in the tool masifest will be initiallized with `TO_BE_PROVIDED` value nad further will have to be provided in the frontend Settings menu.

## Tool Definition Script Example

The `tool_definition` script should always contain a `get_tool` function that returns an instance of the `langchain.agent.Tool` class, as shown in the following example:

```python
from langchain.agents import Tool

def example():
    return "example"

def get_tool(app):
    return Tool(
        name="Example",
        func=example,
        description="This is an example tool."
    ),
```

If any of tool components should use ENV variables, the `get_secret_value` method from internal `utils` module should be used. For example see google search tool definition.

For more examples, refer to the tool definition scripts provided in the example folders.
