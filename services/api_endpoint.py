# fastapi_server.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import utils.logs as logs
from utils.ollama_utility import create_ollama_llm
import uvicorn
from llama_index.core import StorageContext, load_index_from_storage, Settings
import os
import json
import utils.llama_index as llama_index
# from llama_index.core.indices.vector_store import AsyncVectorStoreIndex
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

app = FastAPI()
# Allow CORS for local testing

# Initialize app state variables
app.state.query_engine_RAG = None # Query engine for RAG

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    
    '''
    
    Class to define the request parameters from query
    
    '''

    prompt: str
    top_k_param: int
           
async def create_query_engine(index, top_k):
     
    '''
    Function to create a llama index query engine.
    
    args:
    
    index : The llama index object.
    top_k : int : Retrieve top_k text chunks from the vector index.
    
    ''' 
      
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
       
async def initial_setup(top_k_param):
    '''
    
    Function to setup the ollana LLM model, embedding model and creating a query engine.
    
    '''
    # Read configuration from config.json
    config_path = os.path.join(os.getcwd(), "config" , "config.json")
    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
            logs.log.info("Configuration successfully loaded from config.json")
    except Exception as e:
        logs.log.error(f"Error loading configuration from config.json: {e}")
        raise HTTPException(status_code=500, detail="Error loading configuration from config.json")

    # Setup Ollama LLM and embedding model using the configuration
    # setup_ollama_llm(config["ollama_model"], config["ollama_endpoint"], config["system_prompt"])
    
    # Create an instance of ollama model langugage : 
    try : 
        Settings.llm = await create_ollama_llm(config["ollama_model"], config["ollama_endpoint"], config["system_prompt"])
    except Exception as e:
        logs.log.error(f"Error creating Ollama language model: {e}")
        raise HTTPException(status_code=500, detail="Error creating Ollama language model")
    
    # Create an instance of the emebedding model :
    try : 
        Settings.embed_model = llama_index.setup_embedding_model(
                config.get("embedding_model"),
        )    
    except Exception as e:
        logs.log.error(f"Error setting up embedding model: {e}")
        raise HTTPException(status_code=500, detail="Error setting up embedding model") 
    
    # Load the index from the storage context and create a query engine
    app.state.query_engine_RAG = await load_index(top_k_param)

# Async setup function to load index : 

async def load_index(top_k_param):
    
    '''
    Function to load the vector index from vector_db 
    
    '''
      
    # Load search index from storage
    try:            
        storage_context = StorageContext.from_defaults(persist_dir=os.getcwd() + "/chroma_db")            
        logs.log.info("Chroma index successfully loaded from the storage.")
            
    except Exception as e:
        
        err = f"Error index from Chroma DB , Please check if documents have been loaded and indexed form Math Reasoning RAG app: {e}"
        logs.log.error(f"error: {err}")
        raise HTTPException(status_code=500, detail=err)
    
    # Load the index from the storage context and create a query engine :   
    
    try:
        index = load_index_from_storage(storage_context)    
        # Initialize the query engine with the index and top_k_param : 
        query_engine_RAG = await create_query_engine(index,top_k_param)
        return query_engine_RAG
    except Exception as e:
        logs.log.error(f"Error creating query engine: {e}")
        raise HTTPException(status_code=500, detail="Error creating query engine")
   
@app.post("/api/math-query")
async def query_llamaindex(request: QueryRequest):
    
    logs.log.info(f"Received query request: {request.prompt}")
    logs.log.info(f"Top K parameter: {request.top_k_param}")
    
    # Initial setup for creating a query engine if there is no query running instance available . 
    if app.state.query_engine_RAG is None:
        
        logs.log.info("Query engine is not available for processing the query. Setting up the query engine...")
        await initial_setup(request.top_k_param)
        logs.log.info("Query engine is available for processing the query")
        
    else : 
        logs.log.info("Query engine is available for processing the query")
    # Send the query to the query engine and retrieve the response
    
    try:
        # This will allow concurrent requests to be accepted by FAST API using threads. 
        # It will still use a single instance of the query engine to process the requests. That will save memory as the query engine is loaded only once.
        # Concurrent requests will be processed in parallel using threads 
        
 
        chatbot_response = await run_in_threadpool(app.state.query_engine_RAG.query,request.prompt) 
        logs.log.info(f"Response from query engine: {chatbot_response.response}") 
        if chatbot_response is None:
            logs.log.error(f"Error processing query: {request.prompt}")
            raise HTTPException(status_code=500, detail="Error processing query")
        
        else:
            doc_nodes = await run_in_threadpool(app.state.query_engine_RAG.retrieve,request.prompt)
            logs.log.info(f"Response from query engine: {chatbot_response.response}")
            if hasattr(chatbot_response, 'response') and len(doc_nodes) > 0:
                return {"response": chatbot_response.response, "nodes": doc_nodes}
            else:
                logs.log.error("Response or source nodes missing in chatbot response")
                raise HTTPException(status_code=500, detail="Response or source nodes missing in chatbot response")            
        
    except Exception as e:
        logs.log.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Error processing query")  
    
async def run_fastapi():
    logs.log.info("Starting FastAPI server...")
    config = Config()
    config.bind = ["0.0.0.0:8000"]
    await serve(app, config)

if __name__ == "__main__":
    asyncio.run(run_fastapi())

