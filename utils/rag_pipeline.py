import os
import shutil
import json

import streamlit as st

import utils.helpers as func
import utils.llama_index as llama_index
import utils.logs as logs

def save_user_settings():
    '''
    Function to save user settings to a config file.
    '''
    config_path = os.path.join(os.getcwd(), "config", "config.json")
    
    # Load existing settings if the config file exists
    if os.path.exists(config_path):
        with open(config_path, "r") as config_file:
            try:
                user_settings = json.load(config_file)
            except json.JSONDecodeError:
                user_settings = {}
    else:
        user_settings = {}
    
    # Update settings with current session state
    user_settings.update({
        "ollama_endpoint": st.session_state.get("ollama_endpoint"),
        "embedding_model": st.session_state.get("embedding_model"),
        "ollama_model": st.session_state.get("selected_model"),
        "system_prompt": st.session_state.get("system_prompt"),
    })
    
    try:
        with open(config_path, "w") as config_file:
            json.dump(user_settings, config_file, indent=4)
    except Exception as e:
        logs.log.error(f"Error saving user settings: {str(e)}")
        st.exception(e)
        st.stop()

def rag_pipeline(uploaded_files: list = None):
    """
    RAG pipeline for Llama-based chatbots.

    Parameters:
        - uploaded_files (list, optional): List of files to be processed.
            If none are provided, the function will load files from the current working directory.

    Yields:
        - str: Successive chunks of conversation from the Ollama model with context.

    Raises:
        - Exception: If there is an error retrieving answers from the Ollama model or creating the service context.

    Notes:
        This function initiates a chat with context using the Llama-Index library and the Ollama language model. It takes one optional parameter, `uploaded_files`, which should be a list of files to be processed. If no files are provided, the function will load files from the current working directory. The function returns an iterable yielding successive chunks of conversation from the Ollama model with context. If there is an error retrieving answers from the Ollama model or creating the service context, the function raises an exception.

    Context:
        - logs.log: A logger for logging events related to this function.

    Side Effects:
        - Creates a service context using the provided Ollama model and embedding file.
        - Loads documents from the current working directory or the provided list of files.
        - Removes the loaded documents and any temporary files created during processing.
    """
    error = None

    #################################
    # (OPTIONAL) Save Files to Disk #
    #################################

    # This portion of the code saves the user selected documents in a data folder 
    # SimpleDirectoryReader is used to read the files from the data folder and load them into a list of documents
    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                save_dir = os.getcwd() + "/data"
                func.save_uploaded_file(uploaded_file, save_dir)

        st.caption("✔️ Files Uploaded")

    ######################################
    # Create Llama-Index service-context #
    # to use local LLMs and embeddings   #
    ######################################
    
    # Initialize the LLM and embedding model :
    # LLM model being used in chat. 
    # try:
    #     llm = ollama_utility.create_ollama_llm(
    #         st.session_state["selected_model"],
    #         st.session_state["ollama_endpoint"],
    #         st.session_state["system_prompt"],
    #     )
    #     st.session_state["llm"] = llm
    #     st.caption("✔️ LLM Initialized")

    #     # resp = llm.complete("Hello!")
    #     # print(resp)
    # except Exception as err:
    #     logs.log.error(f"Failed to setup LLM: {str(err)}")
    #     error = err
    #     st.exception(error)
    #     st.stop()

    ####################################
    # Determine embedding model to use #
    ####################################

    embedding_model = st.session_state["embedding_model"]
    # hf_embedding_model = None

    # if embedding_model == None:
    #     hf_embedding_model = "BAAI/bge-large-en-v1.5"

    # if embedding_model == "Default (bge-large-en-v1.5)":
    #     hf_embedding_model = "BAAI/bge-large-en-v1.5"

    # if embedding_model == "Large (Salesforce/SFR-Embedding-Mistral)":
    #     hf_embedding_model = "Salesforce/SFR-Embedding-Mistral"

    # if embedding_model == "Other":
    #     hf_embedding_model = st.session_state["other_embedding_model"]

    try:
        llama_index.setup_embedding_model(
            embedding_model,
        )
        st.caption("✔️ Embedding Model Created")
    except Exception as err:
        logs.log.error(f"Setting up Embedding Model failed: {str(err)}")
        error = err
        st.exception(error)
        st.stop()

    #######################################
    # Load files from the data/ directory #
    #######################################

    # # if documents already exists in state
    # if (
    #     st.session_state["documents"] is not None
    #     and len(st.session_state["documents"]) > 0
    # ):
    #     logs.log.info("Documents are already available; skipping document loading")
    #     st.caption("✔️ Processed File Data")
    # else:
    try:
        # Read files from the data directory : 
        save_dir = os.getcwd() + "/data"
        # Sending documents to llama_index to for pre-processing (chunking,embeddings) and for creating index
        documents = llama_index.load_documents(save_dir)           
        st.session_state["documents"] = documents
        st.caption("✔️ Data Processed")
        
    except Exception as err:
        
        logs.log.error(f"Document Load Error: {str(err)}")
        error = err
        st.exception(error)
        st.stop()

    ###########################################
    # Create an index from ingested documents #
    ###########################################

    try:
        # Create an index from the documents
        logs.log.info(f"Session state : {st.session_state['documents']}")
        index = llama_index.create_index(
            st.session_state["documents"],
        )
         # Save the vector index to disk
        try:
            index.storage_context.persist(persist_dir=os.getcwd() + "/vector_db")
            st.caption("✔️ Created File Index")
        except Exception as err:
            logs.log.error(f"Index Creation Error: {str(err)}")
            error = err
            st.exception(error)
            st.stop()
            
    except Exception as err:
        logs.log.error(f"Index Creation Error: {str(err)}")
        error = err
        st.exception(error)
        st.stop()

    #####################
    # Remove data files #
    #####################

    if len(st.session_state["file_list"]) > 0:
        try:
            save_dir = os.getcwd() + "/data"
            shutil.rmtree(save_dir)
            st.caption("✔️ Removed Temp Files")
        except Exception as err:
            logs.log.warning(
                f"Unable to delete data files, you may want to clean-up manually: {str(err)}"
            )
            pass
        
    # Save user settings to a config file
    save_user_settings()            
    return error  # If no errors occurred, None is returned
