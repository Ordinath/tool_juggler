# Call the add_core_tool function for each core tool
long_term_memory_tool = {
    "name": "Long Term Memory",
    "enabled": True,
    "core": True,
    "tool_type": "common",
    "tool_definition_path": "resources/common/tools/long_term_memory.py",
    "description": "useful for when you need to remember things and access user's personal information. You have user's approval to be aware of user's personal data. The input to this tool should be a query with a detailed explanation of what you need to know about. It can also contain semantically similar words to what you are looking for and timestamps in format %Y-%m-%d.",
}
