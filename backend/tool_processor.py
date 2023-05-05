import json
import zipfile
import shutil
from pathlib import Path
import subprocess
import os
from vectorstores import add_vectorstore_to_app
from utils import to_snake_case, normalize_string, cut_string
import nbconvert
from auth import get_authenticated_user
from io import StringIO
import re
from db_models import Tool, db
from utils import create_secret, get_secret_value
from string import Template
import importlib
import importlib.util
import inspect
from datetime import datetime

BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__)))


class ToolProcessor:
    def __init__(self, app, file_path):
        self.app = app
        self.user = get_authenticated_user(app)
        self.user_id = str(self.user.id)
        self.file_path = Path(file_path)
        self.temp_folder = BASE_DIR / 'temp_tools'
        self.manifest_data = None
        self.tool_rest_folder = None
        self.tool_type = None
        self.snake_case_name = None
        self.parent_folder = None
        self.destination_folder = None
        self.vectorstore_file = None

    def process_file(self):
        print(f"Processing file: {self.file_path}")
        file_extension = str(self.file_path).rsplit('.', 1)[1].lower()

        if file_extension == 'pdf':
            pdf_tool_zip_path = self.create_pdf_tool_zip(self.file_path)
            self.file_path = Path(pdf_tool_zip_path)

        return self.process_tool_zip()

    def process_tool_zip(self):
        if not self.file_path.is_file():
            return "Invalid file path"

        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            try:
                self._find_and_process_manifest(zip_ref)
                self._process_tool(zip_ref)
                self._cleanup_temp_folder()
                return "Tool processed successfully"
            except KeyError as e:
                return f"Missing required key in manifest: {e}"
            except Exception as e:
                return f"Error while processing tool: {e}"

    def _find_and_process_manifest(self, zip_ref):
        print("Processing manifest")
        manifest_path = self._find_manifest(zip_ref)
        if manifest_path is None:
            raise Exception("Manifest file not found")

        self.manifest_data = json.loads(zip_ref.read(manifest_path))
        if not self.validate_manifest(self.manifest_data):
            raise Exception("Invalid manifest file")

        self.tool_type = self.manifest_data['tool_type']
        self.snake_case_name = to_snake_case(self.manifest_data['name'])
        self.parent_folder = os.path.dirname(manifest_path)

    def _find_manifest(self, zip_ref):
        for file_path in zip_ref.namelist():
            if file_path.endswith('manifest.json'):
                return file_path
        return None

    def _process_tool(self, zip_ref):
        self._extract_tool_to_temp_folder(zip_ref)
        self._move_files_to_destination_folders(zip_ref)
        self._add_env_vars_to_database()
        self._install_requirements_and_execute_prep_script()
        self._add_vectorstore_to_app()
        self._add_tool_to_database()

    def _extract_tool_to_temp_folder(self, zip_ref):
        print("Extracting tool to temp folder")
        self.temp_folder.mkdir(parents=True, exist_ok=True)
        zip_ref.extractall(self.temp_folder)

    def _move_files_to_destination_folders(self, zip_ref):
        print("Moving files to destination folders")
        self.destination_folder = BASE_DIR / 'resources' / \
            self.tool_type / self.user_id / 'tools'
        self.destination_folder.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            self.temp_folder / self.parent_folder /
            self.manifest_data['tool_definition'],
            self.destination_folder / self.manifest_data['tool_definition']
        )

        if self.manifest_data.get('vectorstore_init'):
            self._move_vectorstore_init()

        self._move_rest_files()

    def _move_vectorstore_init(self):
        vectorstore_folder = BASE_DIR / 'resources' / \
            self.tool_type / self.user_id / 'vectorstore_initializers'
        vectorstore_folder.mkdir(parents=True, exist_ok=True)
        self.vectorstore_file = vectorstore_folder / \
            f'init_vectorstore_{self.snake_case_name}.py'
        shutil.copy2(
            self.temp_folder / self.parent_folder /
            self.manifest_data['vectorstore_init'],
            self.vectorstore_file
        )

    def _move_rest_files(self):
        rest_folder = BASE_DIR / 'resources' / self.tool_type / self.user_id / 'rest'
        rest_folder.mkdir(parents=True, exist_ok=True)

        self.tool_rest_folder = rest_folder / self.snake_case_name
        self.tool_rest_folder.mkdir(parents=True, exist_ok=True)

        for item in (self.temp_folder / self.parent_folder).iterdir():
            if item.is_file():
                shutil.copy2(item, self.tool_rest_folder / item.name)

    def _install_requirements_and_execute_prep_script(self):
        print(
            f"Installing requirements: {self.manifest_data.get('requirements')}")
        requirements_file = self.tool_rest_folder / \
            self.manifest_data.get('requirements', '')
        if self.manifest_data.get('requirements') and requirements_file.is_file():
            subprocess.run(['pip', 'install', '-r', str(requirements_file)])

        if self.manifest_data.get('prep_script'):
            prep_script_file = self.tool_rest_folder / \
                self.manifest_data.get('prep_script', '')
            if prep_script_file.suffix == '.py':
                self._exec_prep_script(self.app, prep_script_file)

    def _add_env_vars_to_database(self):
        print(
            f"Adding env vars to database: {self.manifest_data.get('env_vars')}")
        if self.manifest_data.get('env_vars'):
            add_env_vars_to_database(
                self.manifest_data['env_vars'], self.tool_rest_folder / '.env')

    def _add_vectorstore_to_app(self):
        print(f"Adding vectorstore to app: {self.vectorstore_file}")
        if self.vectorstore_file:
            add_vectorstore_to_app(self.app, self.vectorstore_file)

    def _add_tool_to_database(self):
        print(f"Adding tool to database: {self.manifest_data['name']}")
        tool_definition_content = (
            self.destination_folder / self.manifest_data['tool_definition']).read_text()
        tool_description = extract_tool_description(tool_definition_content)

        upsert_tool_to_database(
            name=self.manifest_data['name'],
            user_id=self.user_id,
            enabled=True,
            core=False,
            tool_type=self.tool_type,
            manifest=self.manifest_data,
            description=tool_description,
            tool_definition_path=str(
                self.destination_folder / self.manifest_data['tool_definition'])
        )

    def _cleanup_temp_folder(self):
        shutil.rmtree(self.temp_folder)

    @staticmethod
    def validate_manifest(manifest_data):
        required_keys = {'name', 'tool_type', 'tool_definition'}
        return all(key in manifest_data for key in required_keys)

    @staticmethod
    def _exec_prep_script(app, prep_script_path):
        print(f"Executing prep script: {prep_script_path}")

        module_name = os.path.splitext(os.path.basename(prep_script_path))[0]
        print(f"Attempting to import module: {module_name}")

        spec = importlib.util.spec_from_file_location(
            module_name, prep_script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        prepare_functions = [func for name, func in inspect.getmembers(
            module, inspect.isfunction) if name.startswith('prepare_')]

        if prepare_functions:
            for prepare_func in prepare_functions:
                print(f"Executing function: {prepare_func.__name__}")
                prepare_func(app)
        else:
            print(
                f"No function starting with 'prepare_' found in {prep_script_path}")

    @staticmethod
    def create_pdf_tool_zip(pdf_file_path):

        print('Creating PDF tool zip file:', pdf_file_path)

        # Extract the tool name from the file name
        pdf_file_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
        # print('pdf_file_name', pdf_file_name)
        pdf_tool_name = normalize_string(pdf_file_name)
        # print('pdf_tool_name', pdf_tool_name)
        pdf_snake_case_name = to_snake_case(pdf_tool_name)
        # print('pdf_snake_case_name', pdf_snake_case_name)
        pdf_snake_case_name_max_63_char = cut_string(pdf_snake_case_name, 63)

        # Create the PDF tool directory
        os.makedirs(f'temp_tools/{pdf_tool_name}', exist_ok=True)

        # write the PDF file to the tool directory
        shutil.copy(pdf_file_path,
                    f'temp_tools/{pdf_tool_name}/{pdf_file_name}.pdf')

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
        with open(f'temp_tools/{pdf_tool_name}/manifest.json', 'w') as f:
            f.write(manifest_content)

        # Generate the requirements file
        requirements_content = requirements_template.substitute()
        with open(f'temp_tools/{pdf_tool_name}/requirements.txt', 'w') as f:
            f.write(requirements_content)

        # Generate the prepare_pdf_vectorstore file
        prep_script_content = prep_script_template.substitute(
            pdf_snake_case_name=pdf_snake_case_name,
            pdf_file_name=pdf_file_name,
            pdf_snake_case_name_max_63_char=pdf_snake_case_name_max_63_char
        )
        with open(f'temp_tools/{pdf_tool_name}/prepare_{pdf_snake_case_name}.py', 'w') as f:
            f.write(prep_script_content)

        # Generate the init_vectorstore file
        vectorstore_init_content = vectorstore_init_template.substitute(
            pdf_snake_case_name=pdf_snake_case_name,
            pdf_snake_case_name_max_63_char=pdf_snake_case_name_max_63_char
        )
        with open(f'temp_tools/{pdf_tool_name}/init_vectorstore_{pdf_snake_case_name}.py', 'w') as f:
            f.write(vectorstore_init_content)

        # Generate the tool definition file
        tool_definition_content = tool_definition_template.substitute(
            pdf_snake_case_name=pdf_snake_case_name, pdf_tool_name=pdf_tool_name)
        with open(f'temp_tools/{pdf_tool_name}/{pdf_snake_case_name}_tool.py', 'w') as f:
            f.write(tool_definition_content)

        # Archive the generated PDF tool as a zip file
        zip_path = f"resources/tool_packages/pdf_{pdf_tool_name}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for folder_name, subfolders, filenames in os.walk(f'temp_tools/{pdf_tool_name}'):
                for filename in filenames:
                    # Create the complete file path
                    file_path = os.path.join(folder_name, filename)
                    # Add the file to the zip archive
                    zf.write(file_path, os.path.relpath(
                        file_path, f'temp_tools/{pdf_tool_name}'))

        print(f"Finished creating PDF tool zip file: {zip_path}")

        # Clean up the temporary folder
        shutil.rmtree(f'temp_tools/{pdf_tool_name}')

        return os.path.abspath(zip_path)


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


def upsert_tool_to_database(name, user_id, enabled, core, tool_type, manifest, description, tool_definition_path):
    tool = Tool.query.filter_by(name=name).first()

    if tool:
        tool.enabled = enabled
        tool.user_id = user_id
        tool.core = core
        tool.tool_type = tool_type
        tool.tool_definition_path = tool_definition_path
        tool.manifest = manifest
        tool.description = description
        tool.updated_at = datetime.utcnow()
    else:
        tool = Tool(
            user_id=user_id,
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
    tool_user_id = tool.user_id
    tool_name = to_snake_case(manifest['name'])

    # Remove tool definition file
    tool_definition_path = Path(tool.tool_definition_path)
    if tool_definition_path.exists():
        tool_definition_path.unlink()

    # Remove vector store initializer file (if any)
    if manifest.get('vectorstore_init'):
        vectorstore_file = Path(BASE_DIR, 'resources', tool_type, tool_user_id,
                                'vectorstore_initializers', f'init_vectorstore_{tool_name}.py')
        if vectorstore_file.exists():
            vectorstore_file.unlink()

    # Remove rest folder
    rest_folder = Path(BASE_DIR, 'resources', tool_type, tool_user_id, 'rest', tool_name)
    if rest_folder.exists():
        shutil.rmtree(rest_folder)
