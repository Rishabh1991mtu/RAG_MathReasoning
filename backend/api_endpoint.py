# fastapi_server.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import utils.logs as logs
from utils.ollama_utility import context_chat
import streamlit as st
import uvicorn

app = FastAPI()

# Allow CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    prompt: str

@app.post("/api/math-query")
async def query_llamaindex(request: QueryRequest):
    logs.log.info(f"Received query request: {request.prompt}")
    
    try:
        # Retrieve the query engine from Streamlit session state
        query_engine = st.session_state.get("query_engine")
        if not query_engine:
            raise HTTPException(status_code=400, detail="Query engine not initialized")
        response = context_chat(prompt=request.prompt, query_engine=query_engine)        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Function to run FastAPI in a separate process
def run_fastapi():
    logs.log.info("Starting FastAPI server...")
    try : 
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logs.log.error(f"Error starting FastAPI server: {e}")
