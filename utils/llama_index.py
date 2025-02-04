import os

import streamlit as st

import utils.logs as logs

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from llama_index.core.node_parser import SentenceSplitter

# This is not used but required by llama-index and must be set FIRST
os.environ["OPENAI_API_KEY"] = "sk-abc123"


from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
)

global_query_engine = None

###################################
#
# Setup Embedding Model
#
###################################


@st.cache_resource(show_spinner=False)
def setup_embedding_model(
    model: str,
):
    """
    Sets up an embedding model using the Hugging Face library.

    Args:
        model (str): The name of the embedding model to use.

    Returns:
        An instance of the HuggingFaceEmbedding class, configured with the specified model and device.

    Raises:
        ValueError: If the specified model is not a valid embedding model.

    Notes:
        The `device` parameter can be set to 'cpu' or 'cuda' to specify the device to use for the embedding computations. If 'cuda' is used and CUDA is available, the embedding model will be run on the GPU. Otherwise, it will be run on the CPU.
    """
    try:
        from torch import cuda
        device = "cpu" if not cuda.is_available() else "cuda"
    except:
        device = "cpu"
    finally:
        logs.log.info(f"Using {device} to generate embeddings")

    # Settting to use HuggingFaceEmbedding model set by the user.
    # It is being used in the query engine
    try:
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=model,
            device=device,
        )
        logs.log.info(f"Embedding model created successfully")        
        logs.log.info(f"Embedding model is {Settings.embed_model}")
    except Exception as err:
        print(f"Failed to setup the embedding model: {err}")


###################################
#
# Load Documents
#
###################################


def load_documents(data_dir: str):
    """
    Loads documents from a directory of files.

    Args:
        data_dir (str): The path to the directory containing the documents to be loaded.

    Returns:
        A list of documents, where each document is a string representing the content of the corresponding file.

    Raises:
        Exception: If there is an error creating the data index.

    Notes:
        The `data_dir` parameter should be a path to a directory containing files that represent the documents to be loaded. The function will iterate over all files in the directory, and load their contents into a list of strings.
    """
    try:
        # Reads all the files in the data directory and returns a list of documents
        files = SimpleDirectoryReader(input_dir=data_dir, recursive=True)
        documents = files.load_data(files)        
        logs.log.info(f"Loaded {len(documents):,} documents from files")
        return documents
    except Exception as err:
        logs.log.error(f"Error creating data index: {err}")
        raise Exception(f"Error creating data index: {err}")
    finally:
        for file in os.scandir(data_dir):
            if file.is_file() and not file.name.startswith(
                ".gitkeep"
            ):  # TODO: Confirm syntax here
                os.remove(file.path)
        logs.log.info(f"Document loading complete; removing local file(s)")


###################################
#
# Create Document Index
#
###################################


@st.cache_resource(show_spinner=False)
def create_index(_documents):
    """
    Creates an index from the provided documents and service context.
    Splits documents based on chuck size and overlap set by the user.
    
    Args:
        documents (list[str]): A list of strings representing the content of the documents to be indexed.

    Returns:
        An instance of `VectorStoreIndex`, containing the indexed data.

    Raises:
        Exception: If there is an error creating the index.

    Notes:
        The `documents` parameter should be a list of strings representing the content of the documents to be indexed.
    """

    # Updated code to include SentenceSplitter based on chunk size and overlap
    try:
        index = VectorStoreIndex.from_documents(
            documents=_documents, show_progress=True,
            transformations=[SentenceSplitter(chunk_size=st.session_state["chunk_size"],
                                              chunk_overlap=st.session_state["chunk_overlap"],
                                              separator=".",
                                              paragraph_separator='\n\n')],
        )

        logs.log.info("Index created from loaded documents successfully")

        return index
    except Exception as err:
        logs.log.error(f"Index creation failed: {err}")
        raise Exception(f"Index creation failed: {err}")


###################################
#
# Create Query Engine
#
###################################


# @st.cache_resource(show_spinner=False)
def create_query_engine(_documents):
    """
    Creates a query engine from the provided documents and service context.

    Args:
        documents (list[str]): A list of strings representing the content of the documents to be indexed.

    Returns:
        An instance of `QueryEngine`, containing the indexed data and allowing for querying of the data using a variety of parameters.

    Raises:
        Exception: If there is an error creating the query engine.

    Notes:
        The `documents` parameter should be a list of strings representing the content of the documents to be indexed.

        This function uses the `create_index` function to create an index from the provided documents and service context, and then creates a query engine from the resulting index. The `query_engine` parameter is used to specify the parameters of the query engine, including the number of top-ranked items to return (`similarity_top_k`) and the response mode (`response_mode`).
    """
    
    logs.log.info(f"Document list is {_documents[0]}")
    logs.log.info(f"Total documents {len(_documents)}")
    
    try:
        #  Vector index generated from set of documents : 
        index = create_index(_documents)
        
        global_query_engine = index.as_query_engine(
            similarity_top_k=st.session_state["top_k"],
            response_mode=st.session_state["chat_mode"],
            streaming=True,
        )

        # Assigned query engine object to session state. 
        st.session_state["query_engine"] = global_query_engine

        logs.log.info("Query Engine created successfully")

        return global_query_engine
    except Exception as e:
        logs.log.error(f"Error when creating Query Engine: {e}")
        raise Exception(f"Error when creating Query Engine: {e}")
