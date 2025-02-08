# Development and Runtime Setup

# Installation Instructions : 
Before you get started with Local RAG, ensure you have:

- A local [Ollama](https://github.com/ollama/ollama/) instance
- At least one model available within Ollama
    - `llama3:8b` or `llama2:7b` are good starter models
    -  ollama pull llama 3:8b
- Python 3.12 . If python isnt' present -> 
- Run 'ollama list' in terminal to confirm if ollama models are available
- ollama list 
- ollama endpoint : "http://localhost:11434/"
- ollama version : ollama version is 0.5.7

- Setup local environment : 
- `pip install pipenv && pipenv install`  
- `pipenv shell`

**WARNING:** This application is `untested` on Windows Subsystem for Linux. For best results, please utilize a Linux host if possible.

- Steps to launch the Math Reasoning RAG app : 
-  `uvicorn services.api_endpoint:app --reload` App backend - FastAPI , endpoint : "http://127.0.0.1:8000"
-  `streamlit run main.py` : App frontend - Streamlit , endpoint : "http://localhost:8501/"

**NOTE:** Run FastAPI() in 1 terminal and `streamlit run main.py` in another terminal . 
