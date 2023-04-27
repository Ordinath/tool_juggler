#!/bin/bash

# Check Python version
required_python_version="3.10.10"
current_python_version=$(python3.10 --version | awk '{print $2}')
if [ "$current_python_version" != "$required_python_version" ]; then
    echo -e "\033[33mWarning: Python version is $current_python_version, which has not been thoroughly tested. It might encounter errors.\033[0m"
    echo -e "\033[33mIf you encounter any issues, please use Python $required_python_version.\033[0m"
else
    echo "Python version is $required_python_version"
fi

# Backend setup
cd backend
# pwd
python3.10 -m venv venv
source venv/bin/activate
venv/bin/pip install --upgrade pip
venv/bin/pip install --ignore-installed -r requirements.txt 

# Apply fixes to langchain and chroma libraries
langchain_fix="s/return self._generate(messages, stop=stop).generations\[0\].message/output = self._generate(messages, stop=stop)\n        self.callback_manager.on_llm_end(output, verbose=self.verbose)\n        return output.generations[0].message/"
chroma_fix="s/def get_or_create_collection(self, name: str, metadata: Optional\[Dict\] = None) -> Collection:/def get_or_create_collection(\n        self,\n        name: str,\n        metadata: Optional\[Dict\] = None,\n        embedding_function: Optional\[Callable\] = None,\n        ) -> Collection:/"

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "$langchain_fix" venv/lib/python3.10/site-packages/langchain/chat_models/base.py
    sed -i '' "$chroma_fix" venv/lib/python3.10/site-packages/chromadb/api/__init__.py
else
    # Linux
    sed -i "$langchain_fix" venv/lib/python3.10/site-packages/langchain/chat_models/base.py
    sed -i "$chroma_fix" venv/lib/python3.10/site-packages/chromadb/api/__init__.py
fi

echo "Langchain and Chroma libraries fixes applied"

# Frontend setup
cd ../frontend
npm install

# # Print success message and instructions
# echo "Installation complete!"