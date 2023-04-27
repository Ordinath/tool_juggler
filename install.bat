@echo off

REM Check Python version
FOR /F "tokens=* USEBACKQ" %%F IN (`python --version`) DO (
    SET current_python_version=%%F
)
SET required_python_version="Python 3.10.10"
IF NOT "%current_python_version%"=="%required_python_version%" (
    COLOR 0E
    ECHO Warning: Python version is %current_python_version%, which has not been thoroughly tested. It might encounter errors.
    ECHO If you encounter any issues, please use %required_python_version%.
    COLOR
) ELSE (
    ECHO Python version is %required_python_version%
)

REM Backend setup
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

REM Fix langchain library
python -c "import fileinput, sys; s = open(sys.argv[1]).read(); s = s.replace('return self._generate(messages, stop=stop).generations[0].message', 'output = self._generate(messages, stop=stop)\r\n        self.callback_manager.on_llm_end(output, verbose=self.verbose)\r\n        return output.generations[0].message'); open(sys.argv[1], 'w').write(s)" venv\Lib\site-packages\langchain\chat_models\base.py

REM Fix chroma library
python -c "import fileinput, sys; s = open(sys.argv[1]).read(); s = s.replace('def get_or_create_collection(self, name: str, metadata: Optional[Dict] = None) -> Collection:', 'def get_or_create_collection(\r\n        self,\r\n        name: str,\r\n        metadata: Optional[Dict] = None,\r\n        embedding_function: Optional[Callable] = None,\r\n        ) -> Collection:'); open(sys.argv[1], 'w').write(s)" venv\Lib\site-packages\chromadb\api\__init__.py

REM Frontend setup
cd ..\frontend
npm install

REM Print success message and instructions
ECHO Installation complete!