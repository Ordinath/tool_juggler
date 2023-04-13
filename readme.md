## raw and dirty pre-alpfa version - use at own risk

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
`cd venv/lib/python3.10/site-packages/langchain/chat_models`
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


`python app.py`

This should launch backend on [http://localhost:5005](http://localhost:5005)

### Frontend installation/setup and running

frontend/.env.local file required with the following content:
```
NEXT_PUBLIC_OPENAI_API_KEY={your openai api key} # used from frontend to call openai api for voice recognition
NEXT_PUBLIC_OPENAI_API_URL=https://api.openai.com/v1/chat/completions
NEXT_PUBLIC_PY_BACKEND_API_URL=http://localhost:5005
```

`cd frontend`
`npm install`
`npm run dev`

Open [http://localhost:3000](http://localhost:3000) with your browser to see the chat page.
