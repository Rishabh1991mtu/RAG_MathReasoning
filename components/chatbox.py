import streamlit as st
import utils.logs as logs
import requests
from utils.ollama_utility import chat, context_chat
import re


API_URL = "http://localhost:8000/api/math-query"  # FastAPI Endpoint

def format_response_latex(response):
    """
    Function to extract text and latex expressions from a response and render them in Streamlit.

    Args:
        response (str): The response string containing answer from LLM model.
    """
    # Log the original response
    logs.log.info(f"Response: {response}")

    # Regular expression to extract LaTeX expressions inside \[ ... \] blocks
    latex_pattern = r"(.*?)?(\\\[.*?\\\])"

    # Find all text and LaTeX pairs
    matches = re.findall(latex_pattern, response, re.DOTALL)

    for text_part, latex_part in matches:
        if text_part.strip():
            st.write(text_part.strip())  # Display normal text

        if latex_part.strip():
            clean_latex = latex_part.replace("\\[", "").replace("\\]", "").strip()
            st.latex(clean_latex)  # Display LaTeX expression

    # If there is remaining text after the last LaTeX expression, display it
    remaining_text = re.sub(latex_pattern, "", response, flags=re.DOTALL).strip()
    if remaining_text:
        st.write(remaining_text)

def call_fastapi_backend(user_input,top_k,ollama_model,ollama_endpoint,system_prompt, embedding_model):
    """
    Calls the FastAPI backend with the user query and returns the response.
    """
    try:
        response = requests.post(API_URL, json={"prompt": user_input,
                                                "top_k_param": top_k,
                                                "ollama_model":ollama_model,
                                                "ollama_endpoint":ollama_endpoint,
                                                "system_prompt":system_prompt,
                                                "embedding_model":embedding_model})
                                            
        
        response.raise_for_status()  # Raise error for non-200 responses
        return response
    
    except requests.exceptions.RequestException as e:
        st.error(f"API error: {e}")
        return None
       
def chatbox():
    """
    Function to setup chatbox in Streamlit frontent.

    Args:
        None
    """
    if prompt := st.chat_input("How can I help?"):

        # Add the user input to messages state
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Update prompt to explicitly mention to generate response in LaTeX format for better format. 
        # This helps in main
        prompt = f"{prompt} . I would prefer the response in LaTeX format for the math equations "   
        top_k = st.session_state["top_k"] # Retrieve top k value from session state
        ollama_model = st.session_state["selected_model"]
        ollama_endpoint = st.session_state["ollama_endpoint"]
        system_prompt = st.session_state["system_prompt"]   
        embedding_model = st.session_state["embedding_model"]   
        
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                # Call the FastAPI backend to get the response with user prompt and top k values.
                response = call_fastapi_backend(prompt, top_k, ollama_model, ollama_endpoint, system_prompt, embedding_model)
                # response = context_chat(
                #      prompt=prompt, query_engine=st.session_state["query_engine"]
                # )  
        
        logs.log.info(f"Response from FastAPI backend is {response}")
        
        if response:
            response_json = response.json()
            chatbot_response = response_json.get("response", "")
            retrieved_nodes = response_json.get("nodes")
            logs.log.info(f"chatbot_response are {retrieved_nodes}")

            # Render response in latex and markdown language .
            format_response_latex(chatbot_response)
                    
            # # Retrieve the nodes from the query engine based on the user input.       
            # logs.log.info(f"retrieved_nodes total is {len(retrieved_nodes)}")
            
            # # Extract filename and scores from retrieved chunks and create a dictionary for unique file names
            # file_scores_dict = {}
            # for node in retrieved_nodes:
            #     file_name = node.metadata.get('file_name', 'N/A')
            #     score = round(node.score, 3)
            #     if file_name not in file_scores_dict:
            #         file_scores_dict[file_name] = []
            #         file_scores_dict[file_name].append(score)
            #     else: 
            #         file_scores_dict[file_name].append(score)
            
            # citations = "Citations:<br>"       

            # # Display document from which data is retrieved along with scores
            # chunk_index = 1
            # file_index = 1
            # for file_name, scores in file_scores_dict.items():
            #     citations += f"<h4>{file_index}. Filename: {file_name}<h4><br>"
            #     citations += "<table><tr><th>Chunk</th><th>Similarity Score</th></tr>"
            #     file_index += 1
            #     for score in scores:
            #         citations += f"<tr><td>{chunk_index}</td><td>{score}</td></tr>"
            #         chunk_index += 1
            #     citations += "</table><br>"

            # # Send Citations to chat.
            # with st.chat_message("assistant"):
            #     st.markdown(citations, unsafe_allow_html=True)

            # Add the final response to messages state
            st.session_state["messages"].append({"role": "assistant", "content": response})

        

        