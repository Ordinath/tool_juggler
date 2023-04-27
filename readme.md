## alpha version - raw and unpolished

#### https://discord.gg/qzTwvKkc

### Installation and Prerequisites

You can use the automated installation and running process to set up the project. In case this doesn't work for any reason, you can follow the steps provided below for manual installation and running.

#### Automated Installation and Running

To use the automated installation script, run the following command:

```npm install```

This will detect your operating system and execute the appropriate installation script (`install.sh` for Linux/macOS or `install.bat` for Windows).

To start the application automatically, run the following command:

```npm start```

This will start both the backend and frontend and open your browser at [http://localhost:3000](http://localhost:3000).

#### Manual Installation

Follow the steps provided below for manual installation and running if the automated process doesn't work as expected.

##### Backend installation/setup and running

This was tested and ran on Python 3.10.10. Both 3.11 and 3.09 had issues with the langchain and chroma libraries installations.

###### Install dependencies:

```cd backend```

```python3 --version``` # should be 3.10.10

```python3 -m venv venv```

```
# Linux/macOS
source venv/bin/activate
# or Windows
venv\Scripts\activate
```

```pip install -r requirements.txt```

###### Fix issues in libraries:

Replace broken code in langchain library (to properly recognize chat model stream end):

```cd venv/lib/python3.10/site-packages/langchain/chat_models```

Open `base.py` and replace the following code:

```
        return self._generate(messages, stop=stop).generations[0].message
```

with

```
        output = self._generate(messages, stop=stop)
        self.callback_manager.on_llm_end(output, verbose=self.verbose)
        return output.generations[0].message
```

Replace broken code in chroma library (to intake optional embedding_function parameter):

```cd venv/lib/python3.10/site-packages/chromadb/api```

Open `__init__.py` and replace the following code on line 85:

```
    def get_or_create_collection(self, name: str, metadata: Optional[Dict] = None) -> Collection:
```

with

```
    def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[Dict] = None,
        embedding_function: Optional[Callable] = None,
        ) -> Collection:
```

##### Frontend installation/setup and running

```cd frontend```

```npm install```

#### Running the project manually

###### Launch the backend:

```cd backend```

```
# Linux/macOS
source venv/bin/activate
# or Windows
venv\Scripts\activate
```

```python3 app.py```

This should launch the backend on [http://localhost:5005](http://localhost:5005)

###### Launch the frontend:

```cd frontend```

```npm run dev```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the Tool Juggler page.