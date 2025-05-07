# Codebase Analysis with LLM (Flask Web Application)

## Overview

This project is designed to analyze a given codebase by integrating a Large Language Model (LLM), such as OpenAI's GPT-3.5 Turbo, to extract relevant insights from source code files. The application allows users to either upload a local codebase or provide a GitHub repository link, process the files, and generate a structured output in JSON format. The output includes a high-level overview of the project, key methods, method signatures, descriptions, and complexity analysis.

The entire process is containerized using Docker, and the results are stored in MongoDB for easy retrieval.

## Features

- **Codebase Analysis**: The application analyzes source code files, extracting insights such as method signatures, descriptions, complexity, and overall project functionality.
- **LLM Integration**: Utilizes OpenAI GPT-3.5 Turbo for code comprehension and knowledge extraction, adhering to token limits.
- **Chunking**: Code files are split into smaller chunks using Langchain to fit within the LLM's token limits.
- **MongoDB**: Stores code files, code chunks, and analysis results for persistence and quick retrieval.
- **Caching with Redis**: Uses Redis to store previously processed results to avoid reprocessing.
- **Web Interface**: A simple Flask web application allows users to provide a local codebase or GitHub repository link, view the analysis results, and download the JSON output.

## Project Structure
```
/LLM_Based_Codebase_Analyzer
├── /app.py               # Main Flask application
├── /chunker.py           # Code chunking logic using Langchain
├── /code_loader.py       # Load code from provided path (local or GitHub)
├── /db.py                # MongoDB setup and data storage
├── /cache.py             # Redis caching logic
├── /llm_analyzer.py      # Code chunk analysis using LLM
├── /main.py              # Main code for orchestrating LLM analysis
├── /static
│   └── /style.css        # CSS for styling the Flask web interface
├── /templates
│   └── /index.html       # Flask web interface (UI)
├── /Dockerfile           # Dockerfile for containerization
├── /docker-compose.yml   # Docker Compose setup
├── /.env                 # Environment variables (e.g., API keys)
├── /requirements.txt     # Python dependencies
├── /logs                  # Log files for tracking Flask app events
└── /temp                 # To save the cloned repo files in temp folder
```

## Setup & Installation

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- MongoDB and Redis (Docker containers are used in this project)
- OpenAI API key (for GPT-3.5 Turbo)

### 1. Clone the Repository

```bash
git clone https://github.com/samarasimhapeyala/LLM_Based_Codebase_Analyzer.git
cd LLM_Based_Codebase_Analyzer
```
### 2. Install Dependencies

To install the required Python packages, run the following command:

```
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory and add your API keys (e.g., OpenAI API key):

```bash
OPENAI_API_KEY=your_openai_api_key
```
### 4. Docker Setup

The project is containerized using Docker. To set up the application with Docker, run:

```
docker-compose up --build
```

This will start the Flask web application, MongoDB, and Redis (make sure all are setup already) in Docker containers.

### 5. Access the Web Interface

Once the containers are up and running, open your browser and go to:
```
http://localhost:5000
http://127.0.0.1:8000/
```
Here, you can give the local codebase path or provide a GitHub repository URL. The application will process the code and provide an analysis in JSON format.

## 6. Run the Application Without Docker

If you prefer not to use Docker, you can run the application directly on your machine:

1. Install MongoDB and Redis.
2. Set the environment variables for MongoDB and Redis connections.
3. Run the Flask application with:

    ```bash
    python app.py
    ```

4. Then, navigate to `http://localhost:5000` or `http://127.0.0.1:8000/` (configure) in your browser.

## How It Works

- **Codebase Upload**: The user provides a codebase either as a path to a local directory or a GitHub repository URL (preferrably core files path).
- **File Processing**: The code files are loaded into MongoDB, and each file is split into smaller chunks using Langchain.
- **LLM Analysis**: The code chunks are sent to OpenAI's GPT-3.5 Turbo (or another LLM) for analysis. The LLM extracts insights like project purpose, method descriptions, and code complexity etc.
- **Structured Output**: The analysis results are stored in MongoDB and displayed in the web interface in JSON format, with a download button for easy access to download as final_summary.json.

## Limitations

- **Token Limit**: The use of OpenAI GPT-3.5 Turbo is efficient but has a token limit. For larger files, need to explore 4.o models etc.
- **API Cost**: OpenAI's GPT-3.5 API can incur costs depending on usage.
- **Speed**: The application uses GPT-3.5 for faster inference, but alternative models (e.g., GPT-4 or open-source models via Ollama) may be used for more complex tasks but could be slower.
- **Accuracy**: LLMs results maynot be accurate all the times but efficient as of now.

## Future Enhancements

- **Support for More LLMs**: Support for other open-source models such as GPT-4 or models from Ollama could be added for different use cases.
- **More Complex Code Analysis**: Implement more detailed static code analysis techniques (e.g., control flow, data flow analysis) for better understanding.
- **Improved Performance**: Enhance prompt template and using prompt engineering techniques, improve the overall performance after multiple tests and improve the output analysis quality.

## License

This project is licensed under the MIT License.

## Acknowledgements

- OpenAI for GPT-3.5 Turbo
- Langchain for code chunking and integration with LLMs
- MongoDB and Redis for data storage and caching 
- Flask for the web framework

