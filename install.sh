#!/bin/bash

# Check Python version
required_python_version="3.10.10"
current_python_version=$(python --version | awk '{print $2}')
if [ "$current_python_version" != "$required_python_version" ]; then
    echo -e "\033[33mWarning: Python version is $current_python_version, which has not been thoroughly tested. It might encounter errors.\033[0m"
    echo -e "\033[33mIf you encounter any issues, please use Python $required_python_version.\033[0m"
else
    echo "Python version is $required_python_version"
fi

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Fix langchain library
sed -i "s/return self._generate(messages, stop=stop).generations[0].message/output = self._generate(messages, stop=stop)\n        self.callback_manager.on_llm_end(output, verbose=self.verbose)\n        return output.generations[0].message/" venv/lib/python3.10/site-packages/langchain/chat_models/base.py

# Fix chroma library
sed -i "s/def get_or_create_collection(self, name: str, metadata: Optional\[Dict\] = None) -> Collection:/def get_or_create_collection(\n        self,\n        name: str,\n        metadata: Optional\[Dict\] = None,\n        embedding_function: Optional\[Callable\] = None,\n        ) -> Collection:/" venv/lib/python3.10/site-packages/chromadb/api/__init__.py

# Frontend setup
cd ../frontend
npm install

# Print success message and instructions
echo "Installation complete!"