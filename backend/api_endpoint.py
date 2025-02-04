from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.ollama_utility import context_chat
from utils.llama_index import global_query_engine
import utils.logs as logs

app = FastAPI()

class QueryRequest(BaseModel):
    prompt: str

@app.post("/api/math-query")
async def query_llamaindex(request: QueryRequest):
    
    logs.log.info(f"Received query request: {request.prompt}")
    logs.log.info(f"Query Engine : {global_query_engine}")
    
    try:
        response = context_chat(prompt=request.prompt, query_engine=global_query_engine)        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
