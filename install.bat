@echo off

rem Check Python version
set required_python_version=3.10.10
for /f "tokens=2" %%i in ('python3.10 --version') do set current_python_version=%%i
if "%current_python_version%" NEQ "%required_python_version%" (
    echo Warning: Python version is %current_python_version%, which has not been thoroughly tested. It might encounter errors.
    echo If you encounter any issues, please use Python %required_python_version%.
) else (
    echo Python version is %required_python_version%
)

rem Backend setup
cd backend
python3.10 -m venv venv
call venv\Scripts\activate.bat
venv\Scripts\pip install --upgrade pip
venv\Scripts\pip install --ignore-installed -r requirements.txt

rem Apply fixes to langchain and chroma libraries
set "langchain_fix=return self._generate(messages, stop=stop).generations[0].message"
set "langchain_replacement=output = self._generate(messages, stop=stop)^&^&self.callback_manager.on_llm_end(output, verbose=self.verbose)^&^&return output.generations[0].message"
set "chroma_fix=def get_or_create_collection(self, name: str, metadata: Optional[Dict] = None) -> Collection:"
set "chroma_replacement=def get_or_create_collection(^&^&self,^&^&name: str,^&^&metadata: Optional[Dict] = None,^&^&embedding_function: Optional[Callable] = None,^&^&) -> Collection:"

powershell -Command "(Get-Content venv\Lib\site-packages\langchain\chat_models\base.py) -replace '%langchain_fix%', '%langchain_replacement%' | Set-Content venv\Lib\site-packages\langchain\chat_models\base.py"
powershell -Command "(Get-Content venv\Lib\site-packages\chromadb\api\__init__.py) -replace '%chroma_fix%', '%chroma_replacement%' | Set-Content venv\Lib\site-packages\chromadb\api\__init__.py"

echo Langchain and Chroma libraries fixes applied

rem Frontend setup
cd ..\frontend
npm install

@REM @echo off

@REM REM Check Python version
@REM FOR /F "tokens=* USEBACKQ" %%F IN (`python --version`) DO (
@REM     SET current_python_version=%%F
@REM )
@REM SET required_python_version="Python 3.10.10"
@REM IF NOT "%current_python_version%"=="%required_python_version%" (
@REM     COLOR 0E
@REM     ECHO Warning: Python version is %current_python_version%, which has not been thoroughly tested. It might encounter errors.
@REM     ECHO If you encounter any issues, please use %required_python_version%.
@REM     COLOR
@REM ) ELSE (
@REM     ECHO Python version is %required_python_version%
@REM )

@REM REM Backend setup
@REM cd backend
@REM python -m venv venv
@REM call venv\Scripts\activate
@REM pip install -r requirements.txt

@REM REM Fix langchain library
@REM python -c "import fileinput, sys; s = open(sys.argv[1]).read(); s = s.replace('return self._generate(messages, stop=stop).generations[0].message', 'output = self._generate(messages, stop=stop)\r\n        self.callback_manager.on_llm_end(output, verbose=self.verbose)\r\n        return output.generations[0].message'); open(sys.argv[1], 'w').write(s)" venv\Lib\site-packages\langchain\chat_models\base.py

@REM REM Fix chroma library
@REM python -c "import fileinput, sys; s = open(sys.argv[1]).read(); s = s.replace('def get_or_create_collection(self, name: str, metadata: Optional[Dict] = None) -> Collection:', 'def get_or_create_collection(\r\n        self,\r\n        name: str,\r\n        metadata: Optional[Dict] = None,\r\n        embedding_function: Optional[Callable] = None,\r\n        ) -> Collection:'); open(sys.argv[1], 'w').write(s)" venv\Lib\site-packages\chromadb\api\__init__.py

@REM REM Frontend setup
@REM cd ..\frontend
@REM npm install

@REM REM Print success message and instructions
@REM ECHO Installation complete!
