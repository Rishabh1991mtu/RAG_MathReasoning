# fastapi_server.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import utils.logs as logs
from utils.ollama_utility import create_ollama_llm
import streamlit as st
import uvicorn
from llama_index.core import StorageContext, load_index_from_storage, Settings
import os
import utils.llama_index as llama_index

app = FastAPI()
# Allow CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    
    prompt: str
    top_k_param: int
    ollama_model :str
    ollama_endpoint :str
    system_prompt :str
    embedding_model :str

def create_query_engine(index, top_k):
    
    try:
        query_engine = index.as_query_engine(
            similarity_top_k=top_k,
            response_mode="compact",
            streaming=False,  # Set streaming to False
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
    logs.log.info(f"Ollama endpoint: {request.ollama_endpoint}")
    logs.log.info(f"System prompt: {request.system_prompt}")
    logs.log.info(f"Embedding model: {request.embedding_model}")
    
    # Add checks for each request parameter .
    
    # Load the LLM model : 
    try:
        Settings.llm = create_ollama_llm(request.ollama_model.strip(),
                                         request.ollama_endpoint,
                                         request.system_prompt)
        
        logs.log.info("LLM model successfully loaded.")        
            
    except Exception as e:
            
        logs.log.error(f"Error loading LLM model: {e}")
        raise HTTPException(status_code=500, detail="Error loading LLM model") 
    
    # Load embedding model :    
    embedding_model = request.embedding_model
    hf_embedding_model = embedding_model

    if embedding_model == None:
        hf_embedding_model = "BAAI/bge-large-en-v1.5"

    if embedding_model == "Default (bge-large-en-v1.5)":
        hf_embedding_model = "BAAI/bge-large-en-v1.5"

    if embedding_model == "Large (Salesforce/SFR-Embedding-Mistral)":
        hf_embedding_model = "Salesforce/SFR-Embedding-Mistral"

    try:
        Settings.embed_model = llama_index.setup_embedding_model(
            hf_embedding_model,
        )
        
    except Exception as err:
        logs.log.error(f"Setting up Embedding Model failed: {str(err)}")
        error = err
        st.exception(error)
        st.stop()    
    
    # Check if index has been loaded from the disk. If not, then load it from the disk
    try:            
        storage_context = StorageContext.from_defaults(persist_dir=os.getcwd() + "/vector_db")            
        logs.log.info("Index successfully loaded from storage.")
            
    except Exception as e:
            
        logs.log.error(f"Error loading vector DB or index from storage: {e}")
        raise HTTPException(status_code=500, detail="Error loading vector DB or index from storage")
    
    # Load the index from the storage context   
    index = load_index_from_storage(storage_context)
    
    query_engine_RAG = create_query_engine(index,request.top_k_param)
    
    try:
        chatbot_response = query_engine_RAG.query(request.prompt)
        if chatbot_response is None:
            logs.log.error(f"Error processing query: {request.prompt}")
            raise HTTPException(status_code=500, detail="Error processing query")
        
        else:
            doc_nodes = query_engine_RAG.retrieve(request.prompt) 
            logs.log.info(f"Response from query engine: {chatbot_response.response}")
            if hasattr(chatbot_response, 'response') and len(doc_nodes) > 0:
                return {"response": chatbot_response.response, "nodes": doc_nodes}
            else:
                logs.log.error("Response or source nodes missing in chatbot response")
                raise HTTPException(status_code=500, detail="Response or source nodes missing in chatbot response")            
        
    except Exception as e:
        logs.log.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Error processing query")
        
    except Exception as e:
        
        raise HTTPException(status_code=500, detail="Error creating query engine or processing query")
    
# Function to run FastAPI in a separate process
def run_fastapi():
    logs.log.info("Starting FastAPI server...")
    try : 
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logs.log.error(f"Error starting FastAPI server: {e}")

if __name__ == "__main__":
    run_fastapi()