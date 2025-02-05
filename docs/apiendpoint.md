### Backend : FastAPI endpoint

| Setting      | Description                                        | Default                   |
|--------------|----------------------------------------------------|---------------------------|
| Host         | The host address where the FastAPI server will run | http://127.0.0.1:8000     |
| Port         | The port number for the FastAPI server             | 8000                      |
| Reload       | Enable auto-reload for development                 | True                      |
| Access Point | The endpoint to access the math query API          | /api/math-query           |

### Streamlit

| Setting    | Description                                        | Default                   |
|------------|----------------------------------------------------|---------------------------|
| Page Title | The title of the Streamlit application             | RAG Math Reasoning        |
| Host       | The host address where the Streamlit server will run | http://localhost:8501/  |

### Frontend : Example Curl Command

To send a math query to the FastAPI endpoint, you can use the following curl command:

```sh
curl -X POST "http://127.0.0.1:8000/api/math-query" -H "Content-Type: application/json" -d '{
    "prompt": "What is the integral of x^2?",
    "top_k_param": 3,
    "ollama_model": "llama3:8b",
    "ollama_endpoint": "http://localhost:11434/",
    "system_prompt": "You are an AI math assistant. Please answer the question shared by the user.",
    "embedding_model": "BAAI/bge-large-en-v1.5"
}'
```

You can also use : http://127.0.0.1:8000/docs to send math queries formatted in natural language or Latex notations to backend to recieve a response.