import inspect
import os
import glob
import importlib
import importlib.util
from auth import get_authenticated_user


def register_vectorstores(app):
    app.vectorstores = {}
    user = get_authenticated_user()

    private_directory = os.path.join(
        os.path.dirname(
            __file__), 'resources', 'private', user.id, 'vectorstore_initializers'
    )
    common_directory = os.path.join(
        os.path.dirname(__file__), 'resources', 'common'
    )

    # Find all subdirectories with vectorstore_initializers in the common directory
    common_subdirectories = glob.glob(
        f"{common_directory}/*/vectorstore_initializers")

    # Combine common subdirectories and the private directory
    root_directories = common_subdirectories + [private_directory]

    for root_directory in root_directories:
        for dirpath, _, filenames in os.walk(root_directory):
            for file in filenames:
                if file.endswith(".py"):
                    init_script_path = os.path.join(dirpath, file)
                    add_vectorstore_to_app(app, init_script_path)


def add_vectorstore_to_app(app, init_script_path):
    # if there are no vectorstores, we need to initiate them in app
    if not hasattr(app, 'vectorstores'):
        app.vectorstores = {}

    module_name = os.path.splitext(os.path.basename(init_script_path))[0]

    spec = importlib.util.spec_from_file_location(
        module_name, init_script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for name, function in inspect.getmembers(module, inspect.isfunction):
        if name.startswith('init_vectorstore_'):
            vectorstore_name = name.replace('init_vectorstore_', '')
            print(f"Registering vectorstore: {vectorstore_name}")
            with app.app_context():
                app.vectorstores[vectorstore_name] = function(app)
