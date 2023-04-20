import json
import zipfile
import shutil
from pathlib import Path
import subprocess
import os
from vectorstores import add_vectorstore_to_app
from utils import to_snake_case

BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__)))


def process_tool_zip(app, file_path):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        # Find the manifest.json file in the zip file
        manifest_path = None
        for file_path in zip_ref.namelist():
            if file_path.endswith('manifest.json'):
                manifest_path = file_path
                break

        if manifest_path is None:
            return "Manifest file not found"

        try:
            manifest_data = json.loads(zip_ref.read(manifest_path))
            if not validate_manifest(manifest_data):
                return "Invalid manifest file"

            tool_type = manifest_data['tool_type']

            # Extract files to a temporary folder
            temp_folder = BASE_DIR / 'temp_tools'
            temp_folder.mkdir(parents=True, exist_ok=True)
            zip_ref.extractall(temp_folder)

            # Get the parent folder of the manifest file
            parent_folder = os.path.dirname(manifest_path)

            # Move files to the appropriate folder structure
            destination_folder = BASE_DIR / 'resources' / tool_type / 'tools'
            shutil.move(
                temp_folder / parent_folder / manifest_data['tool_definition'], destination_folder)

            vectorstore_file = None
            if manifest_data.get('vectorstore_init'):
                snake_case_name = to_snake_case(manifest_data['name'])
                vectorstore_folder = BASE_DIR / 'resources' / \
                    tool_type / 'vectorstore_initializers'
                vectorstore_file = vectorstore_folder / \
                    f'init_vectorstore_{snake_case_name}.py'
                shutil.move(
                    temp_folder / parent_folder / manifest_data['vectorstore_init'], vectorstore_file)

            # Install requirements and execute prep script if provided
            if manifest_data.get('requirements'):
                subprocess.run([str(BASE_DIR / 'venv' / 'bin' / 'pip'), 'install',
                                '-r', str(temp_folder / parent_folder / manifest_data['requirements'])])

            if manifest_data.get('prep_script'):
                subprocess.run([str(BASE_DIR / 'venv' / 'bin' / 'python'),
                                str(temp_folder / parent_folder / manifest_data['prep_script'])])

            # Add environment variables to .env file
            if manifest_data.get('env_vars'):
                add_env_vars_to_file(
                    manifest_data['env_vars'], BASE_DIR / '.env')

            # Add the new vectorstore to the Flask application context
            if vectorstore_file:
                add_vectorstore_to_app(app, vectorstore_file)

            # Remove temporary folder
            shutil.rmtree(temp_folder)

            return "Tool processed successfully"
        except KeyError as e:
            return f"Missing required key in manifest: {e}"
        except Exception as e:
            return f"Error while processing tool: {e}"


def validate_manifest(manifest_data):
    required_keys = {'name', 'tool_type', 'tool_definition'}
    return all(key in manifest_data for key in required_keys)


def add_env_vars_to_file(env_vars, file_path):
    # Read the current content of the file and store it in a set
    with open(file_path, 'r') as env_file:
        current_env_vars = set(line.strip() for line in env_file.readlines())

    # Write the new environment variables to the file if they don't already exist
    with open(file_path, 'a') as env_file:
        for env_var in env_vars:
            env_var_key = f"{env_var}="
            if env_var_key not in current_env_vars:
                env_file.write(f"{env_var_key}\n")
