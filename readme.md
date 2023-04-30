# Tool Juggler - Alpha Version

![Tool Juggler Demo](https://github.com/Ordinath/tool_juggler/blob/main/raw/assets/tool_juggler_demo_1.gif)

Tool Juggler is an application that allows you to create custom tools for your AI assistant and add them on-the-fly. Share your custom tools and use them seamlessly as you go.

*Special thanks to the [langchain](https://github.com/hwchase17/langchain) and [chromadb](https://github.com/chroma-core/chroma) libraries. Without them, this project wouldn't be possible.*

For instructions and examples on how to create tools, add them to your AI assistant, and seamlessly integrate them, check out the [Tool Uploading Documentation](https://github.com/Ordinath/tool_juggler/blob/main/tool_examples/readme.md#tool-juggler---tool-uploading-documentation).

**Please note: This is the alpha version, which is raw and unpolished. Use it at your own risk. It is not recommended to deploy it on remote servers or cloud providers, as it is not secure in terms of passing information between backend and frontend. Running it locally is safe for execution.**

While it is possible to run Tool Juggler locally without Docker, it is highly recommended to use Docker for convenience. If you choose to run it without Docker, you will need Python 3.10.10 and may have to apply some fixes to the langchain and chromadb libraries.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation and Running](#installation-and-running)
3. [Roadmap](#roadmap)

## Prerequisites

In order to run Tool Juggler, you must have Docker installed. This is the preferred way to run the app as of now. You can download and install Docker from the official website:

[Docker Desktop for Mac and Windows](https://www.docker.com/products/docker-desktop)

[Docker for Linux](https://docs.docker.com/engine/install/)

## Installation and Running

1. Clone the repository:

```bash
git clone https://github.com/Ordinath/tool_juggler.git
```

2. Navigate to the project directory:

```bash
cd tool_juggler
```

3. Install the dependencies:

```bash
npm install
```

4. Build the Docker containers:

```bash
npm run build
```

5. Start the Docker containers:

```bash
npm start
```

This will start both the backend and frontend and open your browser at [http://localhost:3000](http://localhost:3000).

## Roadmap

The following features are planned or have been completed:

- [x] PDF question and answer tool auto-generation
- [ ] Proper login authentication for multiple users to use the application with a single backend
- [ ] Secure handling of secrets for backend and frontend, allowing deployment on remote servers
- [ ] Native compatibility for uploading CSV files and auto-generating CSV data analysis tools
- [ ] Adding semi-autonomous agents along with conversations, capable of being added on-the-fly as packages and supplied with tools
- [ ] Responsive design for frontend to support convenient usage on mobile devices
- [ ] Add support of non-OpenAI models in long-term
