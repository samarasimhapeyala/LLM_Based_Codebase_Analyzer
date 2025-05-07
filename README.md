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
/codebase-analyzer
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
└── /logs                 # Log files for tracking Flask app events
```
