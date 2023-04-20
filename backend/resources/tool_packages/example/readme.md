
The goal of this task is to implement a solution for uploading, processing, and integrating a custom tool in a Python Flask project, while handling any required environment variables. The tool should be packaged as a zip archive containing the following files:

Tool definition Python script
Manifest JSON file
Vector store initialization Python script (if required)
requirements.txt for pip installs
Any additional files (if necessary)

The manifest JSON file should provide the following information:

Whether the tool is a common or private tool
If a vector store is needed
A link to the tool's Python script
A list of required environment variables for the tool's proper execution
The frontend should provide a dedicated space for users to upload the zip archive of the tool. Upon upload, the backend should process the tool as follows:

Send the uploaded zip archive to a dedicated Python Flask application endpoint
Unpack the zip archive and save the contents to a dedicated "unpacked tools" folder in the backend
Process the manifest file and distribute the tool's files across the Flask project as necessary
Install any required dependencies specified in the requirements.txt file within the Flask virtual environment
Restart the Flask application to ensure the newly added tool is available and functional
In addition to the above steps, the system should provide a mechanism for users to input the required environment variables before using the tool. The manifest file should list the names of these variables, and the system should prompt the user to provide the necessary values.
This task will enable users to upload custom tools to the project, expanding its functionality and versatility, while ensuring proper configuration of environment variables for tool execution.


## below is the v1 basic manifest.json template example from the example tool

```json
{
    "name": "example",
    "tool_type": "common",
    "tool_definition": "example.py",
    "requirements": "requirements.txt",
    "vectorstore_init": null, // or *.py
    "prep_script": "example_prep.py", // can also be *.ipynb or null
    "env_vars": [
        "EXAMPLE_VAR",
        "EXAMPLE_VAR_2"
    ]
}
```
