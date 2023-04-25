import inspect
import os
import importlib
import importlib.util


def register_vectorstores(app):
    vectorstores = {}

    root_directories = [
        os.path.join(os.path.dirname(__file__), 'resources',
                     'common', 'vectorstore_initializers'),
        os.path.join(os.path.dirname(__file__), 'resources',
                     'private', 'vectorstore_initializers'),
    ]

    for root_directory in root_directories:
        # Recursively walk through all nested subdirectories
        for dirpath, _, filenames in os.walk(root_directory):
            # Iterate over all files in the directory
            for file in filenames:
                if file.endswith(".py"):
                    init_script_path = os.path.join(dirpath, file)

                    # Import the init script module
                    module_name = os.path.splitext(
                        os.path.basename(init_script_path))[0]

                    spec = importlib.util.spec_from_file_location(
                        module_name, init_script_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Iterate over all functions defined in the module
                    for name, function in inspect.getmembers(module, inspect.isfunction):
                        # If the function name starts with 'init_vectorstore_', call the function and store the result
                        if name.startswith('init_vectorstore_'):
                            vectorstore_name = name.replace(
                                'init_vectorstore_', '')

                            with app.app_context():
                                vectorstores[vectorstore_name] = function(app)

    app.vectorstores = vectorstores


def add_vectorstore_to_app(app, init_script_path):
    print(f"Registering vectorstore: {init_script_path}")

    # Import the init script module
    module_name = os.path.splitext(os.path.basename(init_script_path))[0]
    print(f"Attempting to import module: {module_name}")

    spec = importlib.util.spec_from_file_location(
        module_name, init_script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Iterate over all functions defined in the module
    for name, function in inspect.getmembers(module, inspect.isfunction):
        # If the function name starts with 'init_vectorstore_', call the function and store the result
        if name.startswith('init_vectorstore_'):
            vectorstore_name = name.replace('init_vectorstore_', '')
            with app.app_context():
                app.vectorstores[vectorstore_name] = function(app)
