import json
import zipfile
import shutil
from pathlib import Path
import subprocess
import os
from vectorstores import add_vectorstore_to_app
from utils import to_snake_case
import nbconvert

BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__)))


def process_tool_zip(app, file_path):
    file_path = Path(file_path)
    if not file_path.is_file():
        return "Invalid file path"

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
            snake_case_name = to_snake_case(manifest_data['name'])

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
                vectorstore_folder = BASE_DIR / 'resources' / \
                    tool_type / 'vectorstore_initializers'
                vectorstore_file = vectorstore_folder / \
                    f'init_vectorstore_{snake_case_name}.py'
                shutil.move(
                    temp_folder / parent_folder / manifest_data['vectorstore_init'], vectorstore_file)

            # Create a 'rest' folder with the same path as the tool and vector store
            rest_folder = BASE_DIR / 'resources' / tool_type / 'rest'
            rest_folder.mkdir(parents=True, exist_ok=True)

            # Create a folder with the tool name in snake_case inside the 'rest' folder
            tool_rest_folder = rest_folder / snake_case_name
            tool_rest_folder.mkdir(parents=True, exist_ok=True)

            # Move all the files from the temporary folder to the tool_rest_folder
            for item in (temp_folder / parent_folder).iterdir():
                if item.is_file():
                    shutil.move(item, tool_rest_folder / item.name)

            # Install requirements and execute prep script if provided
            requirements_file = tool_rest_folder / \
                manifest_data.get('requirements', '')
            if manifest_data.get('requirements') and requirements_file.is_file():
                subprocess.run([str(BASE_DIR / 'venv' / 'bin' / 'pip'), 'install',
                                '-r', str(requirements_file)])

            if manifest_data.get('prep_script'):
                prep_script_file = tool_rest_folder / \
                    manifest_data.get('prep_script', '')

                # Check if the prep script is a Jupyter notebook
                if prep_script_file.suffix == '.ipynb':
                    # Convert the Jupyter notebook to a Python script
                    converted_script_file = prep_script_file.with_suffix('.py')
                    with open(converted_script_file, 'w', encoding='utf-8') as converted_script:
                        nbconvert.export(nbconvert.PythonExporter, str(
                            prep_script_file), output=converted_script)

                    # Execute the converted Python script
                    subprocess.run(
                        [str(BASE_DIR / 'venv' / 'bin' / 'python'), str(converted_script_file)])
                elif prep_script_file.suffix == '.py':
                    # Execute the Python script directly
                    subprocess.run(
                        [str(BASE_DIR / 'venv' / 'bin' / 'python'), str(prep_script_file)])

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
    # Create the .env file if it doesn't exist
    file_path.touch(exist_ok=True)
    # Read the current content of the file and store it in a set
    with open(file_path, 'r') as env_file:
        current_env_vars = set(line.strip() for line in env_file.readlines())

    # Write the new environment variables to the file if they don't already exist
    with open(file_path, 'a') as env_file:
        for env_var in env_vars:
            env_var_key = f"{env_var}="
            if env_var_key not in current_env_vars:
                env_file.write(f"{env_var_key}\n")
