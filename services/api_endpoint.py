# fastapi_server.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import utils.logs as logs
from utils.ollama_utility import create_ollama_llm
import uvicorn
from llama_index.core import StorageContext, load_index_from_storage, Settings
import os
import json
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

query_engine_RAG = None

class QueryRequest(BaseModel):
    
    '''
    
    Class to define the request parameters from query
    
    '''

    prompt: str
    top_k_param: int
    
def setup_ollama_llm(ollama_model, ollama_endpoint, system_prompt):
    
    '''
    
    Function to setup the Ollama LLM model.
    
    args:
    
    ollama_model : str : The name of the Ollama model.
    ollama_endpoint : str : The Ollama endpoint.
    system_prompt : str : The system prompt.
    
    '''
    
    try:
        Settings.llm = create_ollama_llm(ollama_model, ollama_endpoint, system_prompt)
        
    except Exception as err:
        logs.log.error(f"Setting up Ollama LLM failed: {str(err)}")
        raise Exception(f"Setting up Ollama LLM failed: {str(err)}")

def setup_embedding_model(embedding_model):
    
    '''
    
    Function to setup the embedding model.
    
    args:
    
    hf_embedding_model : str : The name of the embedding set in UI .
    
    '''
       
    try:
        Settings.embed_model = llama_index.setup_embedding_model(
            embedding_model,
        )
        
    except Exception as err:
        logs.log.error(f"Setting up Embedding Model failed: {str(err)}")
        raise Exception(f"Setting up Embedding Model failed: {str(err)}")
        
def create_query_engine(index, top_k):
     
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

def load_index(top_k_param):
    
    '''
    Function to load the vector index from vector_db 
    
    '''
      
    # Load search index from storage
    try:            
        storage_context = StorageContext.from_defaults(persist_dir=os.getcwd() + "/vector_db")            
        logs.log.info("Index successfully loaded from storage.")
            
    except Exception as e:
        
        err = f"Error loading vector DB or index from storage , Please check if documents have been loaded and indexed form Math Reasoning RAG app: {e}"
        logs.log.error(f"error: {err}")
        raise HTTPException(status_code=500, detail=err)
    
    # Load the index from the storage context and create a query engine :   
    
    try:
        index = load_index_from_storage(storage_context)    
        query_engine_RAG = create_query_engine(index,top_k_param)
        return query_engine_RAG
    except Exception as e:
        logs.log.error(f"Error creating query engine: {e}")
        raise HTTPException(status_code=500, detail="Error creating query engine")
        
def initial_setup(top_k_param):
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
    setup_ollama_llm(config["ollama_model"], config["ollama_endpoint"], config["system_prompt"])
    setup_embedding_model(config.get("embedding_model"))
    
    # Load the index from the storage context and create a query engine
    query_engine_RAG = load_index(top_k_param)
    # Inital setup is successful 
    initial_setup_flag = True
    return query_engine_RAG
    
@app.post("/api/math-query")
async def query_llamaindex(request: QueryRequest):
    
    global query_engine_RAG
    
    logs.log.info(f"Received query request: {request.prompt}")
    logs.log.info(f"Top K parameter: {request.top_k_param}")
    
    # Initial setup for creating a query engine if there is no query running instance available . 
    if query_engine_RAG is None: 
        logs.log.info("Query engine is not available for processing the query. Setting up the query engine...")
        query_engine_RAG = initial_setup(request.top_k_param)
        logs.log.info("Query engine is available for processing the query")
    else : 
        logs.log.info("Query engine is available for processing the query")
    # Send the query to the query engine and retrieve the response
    
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
    
# Function to run FastAPI in a separate process
def run_fastapi():
    logs.log.info("Starting FastAPI server...")
    try : 
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logs.log.error(f"Error starting FastAPI server: {e}")

if __name__ == "__main__":
    run_fastapi()