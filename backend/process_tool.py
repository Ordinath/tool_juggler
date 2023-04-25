import json
import zipfile
import shutil
from pathlib import Path
import subprocess
import os
from vectorstores import add_vectorstore_to_app
from utils import to_snake_case, normalize_string
import nbconvert
from io import StringIO
import re
from db_models import Tool, db
from utils import create_secret, get_secret_value
from string import Template
import importlib
import importlib.util
import inspect

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

            # Extract the tool description from the tool definition file
            tool_definition_path = os.path.join(os.path.dirname(
                manifest_path), manifest_data['tool_definition'])
            tool_definition_content = zip_ref.read(
                tool_definition_path).decode("utf-8")
            tool_description = extract_tool_description(
                tool_definition_content)

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
            destination_folder.mkdir(parents=True, exist_ok=True)
            destination_tool_definition_path = destination_folder / \
                manifest_data['tool_definition']
            shutil.move(
                temp_folder / parent_folder / manifest_data['tool_definition'], destination_folder, copy_function=shutil.copy2)

            vectorstore_file = None
            if manifest_data.get('vectorstore_init'):
                vectorstore_folder = BASE_DIR / 'resources' / \
                    tool_type / 'vectorstore_initializers'
                vectorstore_folder.mkdir(parents=True, exist_ok=True)
                vectorstore_file = vectorstore_folder / \
                    f'init_vectorstore_{snake_case_name}.py'
                shutil.move(
                    temp_folder / parent_folder / manifest_data['vectorstore_init'], vectorstore_file, copy_function=shutil.copy2)

            # Create a 'rest' folder with the same path as the tool and vector store
            rest_folder = BASE_DIR / 'resources' / tool_type / 'rest'
            rest_folder.mkdir(parents=True, exist_ok=True)

            # Create a folder with the tool name in snake_case inside the 'rest' folder
            tool_rest_folder = rest_folder / snake_case_name
            tool_rest_folder.mkdir(parents=True, exist_ok=True)

            # Move all the files from the temporary folder to the tool_rest_folder
            for item in (temp_folder / parent_folder).iterdir():
                if item.is_file():
                    shutil.move(item, tool_rest_folder / item.name,
                                copy_function=shutil.copy2)

            # Install requirements and execute prep script if provided
            requirements_file = tool_rest_folder / \
                manifest_data.get('requirements', '')
            if manifest_data.get('requirements') and requirements_file.is_file():
                subprocess.run([str(BASE_DIR / 'venv' / 'bin' / 'pip'), 'install',
                                '-r', str(requirements_file)])

            # Add environment variables to .env file
            if manifest_data.get('env_vars'):
                add_env_vars_to_database(
                    manifest_data['env_vars'], tool_rest_folder / '.env')

            if manifest_data.get('prep_script'):
                prep_script_file = tool_rest_folder / \
                    manifest_data.get('prep_script', '')
                
                print('attempting to execute prep script: ', prep_script_file)

                if prep_script_file.suffix == '.py':
                    # Execute the Python script directly
                    exec_prep_script(app, prep_script_file)

            # Add the new vectorstore to the Flask application context
            if vectorstore_file:
                add_vectorstore_to_app(app, vectorstore_file)

            # Add the new tool to the database
            add_tool_to_database(
                name=manifest_data['name'],
                enabled=True,
                core=False,
                tool_type=tool_type,
                manifest=manifest_data,
                description=tool_description,
                tool_definition_path=str(destination_tool_definition_path)
            )

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


def add_env_vars_to_database(env_vars, env_file_path):
    tool_env_vars = {}
    if env_file_path.exists():
        with env_file_path.open() as f:
            for line in f:
                name, value = line.strip().split('=', 1)
                tool_env_vars[name] = value

    for var_name in env_vars:
        if get_secret_value(var_name) is None:
            env_value = tool_env_vars.get(var_name)
            if env_value is not None:
                create_secret(var_name, env_value)
            else:
                create_secret(var_name, 'TO_BE_PROVIDED')


def extract_tool_description(script_content):
    description_pattern = re.compile(
        r"Tool\s*\([^\)]*description\s*=\s*\"([^\"]+)\"")
    match = description_pattern.search(script_content)

    if match:
        return match.group(1)
    return None


def add_tool_to_database(name, enabled, core, tool_type, manifest, description, tool_definition_path):
    tool = Tool(
        name=name,
        enabled=enabled,
        core=core,
        tool_type=tool_type,
        tool_definition_path=tool_definition_path,
        manifest=manifest,
        description=description
    )
    db.session.add(tool)
    db.session.commit()


def remove_tool_files(tool):
    manifest = tool.manifest
    tool_type = tool.tool_type
    tool_name = to_snake_case(manifest['name'])

    # Remove tool definition file
    tool_definition_path = Path(tool.tool_definition_path)
    if tool_definition_path.exists():
        tool_definition_path.unlink()

    # Remove vector store initializer file (if any)
    if manifest.get('vectorstore_init'):
        vectorstore_file = Path(BASE_DIR, 'resources', tool_type,
                                'vectorstore_initializers', f'init_vectorstore_{tool_name}.py')
        if vectorstore_file.exists():
            vectorstore_file.unlink()

    # Remove rest folder
    rest_folder = Path(BASE_DIR, 'resources', tool_type, 'rest', tool_name)
    if rest_folder.exists():
        shutil.rmtree(rest_folder)


def create_pdf_tool_zip(pdf_file_path):

    # Extract the tool name from the file name
    pdf_file_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
    print('pdf_file_name', pdf_file_name)
    pdf_tool_name = normalize_string(pdf_file_name)
    print('pdf_tool_name', pdf_tool_name)
    pdf_snake_case_name = to_snake_case(pdf_tool_name)
    print('pdf_snake_case_name', pdf_snake_case_name)

    # Create the PDF tool directory
    os.makedirs(f'temp/{pdf_tool_name}', exist_ok=True)

    # write the PDF file to the tool directory
    shutil.copy(pdf_file_path, f'temp/{pdf_tool_name}/{pdf_file_name}.pdf')

    # Read the templates and auto-generate the required files
    with open('tool_templates/pdf/manifest_template.json', 'r') as f:
        manifest_template = Template(f.read())
    with open('tool_templates/pdf/requirements_template.txt', 'r') as f:
        requirements_template = Template(f.read())
    with open('tool_templates/pdf/prepare_pdf_vectorstore_template.py', 'r') as f:
        prep_script_template = Template(f.read())
    with open('tool_templates/pdf/init_vectorstore_template.py', 'r') as f:
        vectorstore_init_template = Template(f.read())
    with open('tool_templates/pdf/tool_definition_template.py', 'r') as f:
        tool_definition_template = Template(f.read())

    # Generate the manifest file
    manifest_content = manifest_template.substitute(
        tool_name=pdf_tool_name, pdf_snake_case_name=pdf_snake_case_name)
    with open(f'temp/{pdf_tool_name}/manifest.json', 'w') as f:
        f.write(manifest_content)

    # Generate the requirements file
    requirements_content = requirements_template.substitute()
    with open(f'temp/{pdf_tool_name}/requirements.txt', 'w') as f:
        f.write(requirements_content)

    # Generate the prepare_pdf_vectorstore file
    prep_script_content = prep_script_template.substitute(
        pdf_snake_case_name=pdf_snake_case_name, pdf_file_name=pdf_file_name)
    with open(f'temp/{pdf_tool_name}/prepare_pdf_{pdf_snake_case_name}.py', 'w') as f:
        f.write(prep_script_content)

    # Generate the init_vectorstore file
    vectorstore_init_content = vectorstore_init_template.substitute(
        pdf_snake_case_name=pdf_snake_case_name)
    with open(f'temp/{pdf_tool_name}/init_vectorstore_{pdf_snake_case_name}.py', 'w') as f:
        f.write(vectorstore_init_content)

    # Generate the tool definition file
    tool_definition_content = tool_definition_template.substitute(
        pdf_snake_case_name=pdf_snake_case_name, pdf_tool_name=pdf_tool_name)
    with open(f'temp/{pdf_tool_name}/{pdf_snake_case_name}.py', 'w') as f:
        f.write(tool_definition_content)

    # Archive the generated PDF tool as a zip file
    zip_path = f"resources/tool_packages/pdf_{pdf_tool_name}.zip"
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for folder_name, subfolders, filenames in os.walk(f'temp/{pdf_tool_name}'):
            for filename in filenames:
                # Create the complete file path
                file_path = os.path.join(folder_name, filename)
                # Add the file to the zip archive
                zf.write(file_path, os.path.relpath(
                    file_path, f'temp/{pdf_tool_name}'))

    # Clean up the temporary folder
    shutil.rmtree(f'temp/{pdf_tool_name}')

    return os.path.abspath(zip_path)


def exec_prep_script(app, prep_script_path):
    print(f"Executing prep script: {prep_script_path}")

    # Import the prep script module
    module_name = os.path.splitext(os.path.basename(prep_script_path))[0]
    print(f"Attempting to import module: {module_name}")

    spec = importlib.util.spec_from_file_location(
        module_name, prep_script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find and execute functions starting with 'prepare_'
    prepare_functions = [func for name, func in inspect.getmembers(
        module, inspect.isfunction) if name.startswith('prepare_')]

    if prepare_functions:
        for prepare_func in prepare_functions:
            print(f"Executing function: {prepare_func.__name__}")
            prepare_func(app)
    else:
        print(
            f"No function starting with 'prepare_' found in {prep_script_path}")
