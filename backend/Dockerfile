# Use the official Python image as the base image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Apply fixes to langchain and chroma libraries
RUN sed -i 's/return self._generate(messages, stop=stop).generations\[0\].message/output = self._generate(messages, stop=stop)\n        self.callback_manager.on_llm_end(output, verbose=self.verbose)\n        return output.generations[0].message/' $(python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")/langchain/chat_models/base.py
RUN sed -i 's/def get_or_create_collection(self, name: str, metadata: Optional\[Dict\] = None) -> Collection:/def get_or_create_collection(\n        self,\n        name: str,\n        metadata: Optional\[Dict\] = None,\n        embedding_function: Optional\[Callable\] = None,\n        ) -> Collection:/' $(python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")/chromadb/api/__init__.py

# Expose the port the backend will run on
EXPOSE 5005

# Start the backend
CMD flask run -h 0.0.0.0 -p 5005
