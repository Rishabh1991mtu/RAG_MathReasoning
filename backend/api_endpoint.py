# fastapi_server.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import utils.logs as logs
from utils.ollama_utility import chat,context_chat
import streamlit as st
import uvicorn
from llama_index.core import StorageContext, load_index_from_storage, Settings
import os

app = FastAPI()
storage_context = None # Global variable to keep track of exising index . 

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
    top_k_param: int
    ollama_model :str

def create_query_engine(index,top_k):
    
    try : 
        query_engine = index.as_query_engine(
            similarity_top_k=top_k,
            response_mode="compact",
            streaming=True,
        )
        return query_engine
    except Exception as e:
        logs.log.error(f"Error creating query engine: {e}")
        raise Exception(f"Error creating query engine: {e}")

@app.post("/api/math-query")
async def query_llamaindex(request: QueryRequest):
    
    logs.log.info(f"Received query request: {request.prompt}")
    logs.log.info(f"Top K parameter: {request.top_k_param}")
    logs.log.info(f"Ollama model: {request.ollama_model}")

    global storage_context  # Ensure we modify the global storage_context

    # Check if index has been loaded from the disk. If not, then load it from the disk
    if storage_context is None:
        try:            
            storage_context = StorageContext.from_defaults(persist_dir=os.getcwd() + "/vector_db")
            #service_context = ServiceContext.from_defaults(llm=None)
            #index = load_index_from_storage(storage_context, service_context=service_context)
            index = load_index_from_storage(storage_context)
            logs.log.info("Index successfully loaded from storage.")
            
        except Exception as e:
            
            logs.log.error(f"Error loading vector DB or index from storage: {e}")
            raise HTTPException(status_code=500, detail="Error loading vector DB or index from storage")

    try:
        query_engine_RAG = create_query_engine(index,request.top_k_param)
        response = context_chat(prompt=request.prompt, query_engine=query_engine_RAG)
        if response is None:
            
            logs.log.error(f"Error processing query: {request.prompt}")
            raise HTTPException(status_code=500, detail="Error processing query")
        
    except Exception as e:
        
        logs.log.error(f"Error creating query engine or processing query: {e}")
        raise HTTPException(status_code=500, detail="Error creating query engine or processing query")

    return response
    
# Function to run FastAPI in a separate process
def run_fastapi():
    logs.log.info("Starting FastAPI server...")
    try : 
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logs.log.error(f"Error starting FastAPI server: {e}")

if __name__ == "__main__":
    run_fastapi()