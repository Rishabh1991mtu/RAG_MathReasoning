#!/bin/bash

# Function to run the FastAPI backend : 

run_fastapi() {
    echo "Running FastAPI backend"
    uvicorn services.api_endpoint:app --workers 16
}

# Function to run the Streamlit frontend
run_streamlit() {
    echo "Starting Streamlit frontend..."
    streamlit run main.py 
}

# Run both FastAPI and Streamlit in parallel
run_fastapi &
run_streamlit &

# Wait for both processes to finish
wait