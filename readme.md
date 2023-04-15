## raw and dirty pre-alpha version - use at own risk

### High-level goals from the top of the head:

#### Refactor Backend app.py
- Extract tools functionality into dedicated 'common' and 'internal' folders
- Ensure 'internal' folder is gitignored
- Move common tools (simple Python functions with metadata) to the 'common' folder
- Refactoring and logic extraction of other functionality from app.py into dedicated files
- Make ai responce endpoint to properly consume stream parameter for backend decoupling

#### Add Message frontend CRUD support Functionality
- Implement message editing and deletion on the frontend (all types of messages)

#### Improve Final Awnser parsing with proper regex
- Make code blocks properly rendered on frontend
- Potentially implement token buffer for proper handling of frontend rendering via streaming

#### On-demand Embeddings for Conversations
- Add functionality to create embeddings for specific conversations from a frontend request
- Store embeddings in a vector base
- Indicate conversations with embeddings on the frontend
- Add common tooling to pull the previous conversation memory into scope on demand
- Addition of time awareness 

#### Frontend Control of Enabled/Disabled Tools
- Create a lower left sidebar section to display available tools
- Have tool table (with all relevant info) in local SQLite database
- Enable/disable tools based on frontend application state upon ai completion requests
- Send enabled tools with AI completion requests to the backend

#### Attachments and File Handling
- Enable attaching pictures and files (PDF/DOC/etc) to conversations
- Discuss architectural decisions for handling attachments on frontend
- Determine how to embed or supply attachments to tools as context
- make common tooling to get pictures from DALL-e upon query

#### Plugin and Tool Juggler Functionality
- Implement capability to supply backend AI with tooling from chat (JSON with all required data)
- Create dedicated tool for adding other tools on the fly
- Plan architectural decisions for this epic level task 

## Installation and Prerequisites

### Backend installation/setup and running

this was tested and ran on python 3.10.10, both 3.11 and 3.09 had issues with the langchain and chroma libraries installations.

prepare environment variables - create .env file in backend folder with the following content:
```
OPENAI_API_KEY={your openai api key}
GOOGLE_API_KEY={your google custom search engine api key}
GOOGLE_CSE_ID={your google custom search engine id}
NS_CLIENT_KEY={for netsuite related stuff}
NS_CLIENT_SECRET={for netsuite related stuff}
NS_RESOURCE_OWNER_KEY={for netsuite related stuff}
NS_RESOURCE_OWNER_SECRET={for netsuite related stuff}
NS_REALM={for netsuite related stuff}
```

install dependencies:

```cd backend```

```python --version``` # should be 3.10.10

```python -m venv venv```

```
# Linux/macOS
source venv/bin/activate
# or Windows
venv\Scripts\activate
```

`pip install -r requirements.txt`

the fun part - replace broken code in langchain library (to properly recognize chat model stream end):

```cd venv/lib/python3.10/site-packages/langchain/chat_models```

open base.py and replace the following code:

```
return self._generate(messages, stop=stop).generations[0].message # line 128
```

with

```
output = self._generate(messages, stop=stop)
self.callback_manager.on_llm_end(output, verbose=self.verbose)
return output.generations[0].message
```

to launch:

```python app.py```

This should launch backend on [http://localhost:5005](http://localhost:5005)

### Frontend installation/setup and running

frontend/.env.local file required with the following content:
```
NEXT_PUBLIC_OPENAI_API_KEY={your openai api key} # used from frontend to call openai api for voice recognition
NEXT_PUBLIC_OPENAI_API_URL=https://api.openai.com/v1/chat/completions
NEXT_PUBLIC_PY_BACKEND_API_URL=http://localhost:5005
```

```cd frontend```

```npm install```

```npm run dev```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the chat page.
