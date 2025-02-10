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

To send a math query to the FastAPI endpoint, you can use the following curl command and in shell terminal:

Option 1 : Run directly in terminal : 
```sh
curl -X POST "http://127.0.0.1:8000/api/math-query" -H "Content-Type: application/json" -d '{
    "prompt": "What is the integral of x^2?",
    "top_k_param": 3,
}
```

Options 2: 
- Open PowerShell cd to to services folder in your Math RAG code location. Execute the following commands : 
```sh
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
./math_query.ps1  
```

For testing : You can also use : http://127.0.0.1:8000/docs to test the API endpoint . 