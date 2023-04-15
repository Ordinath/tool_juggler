import os
import importlib

def discover_tools(folders):
    tools = []

    for folder in folders:
        for filename in os.listdir(folder.replace(".", "/")):
            if not filename.endswith(".py") or filename.startswith("__"):
                continue

            module_name = filename[:-3]
            module_path = f"{folder}.{module_name}"
            module = importlib.import_module(module_path)
            tool = module.get_tool()
            tools.extend(tool)

    return tools

