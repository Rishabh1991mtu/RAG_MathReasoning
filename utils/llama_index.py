import os

import streamlit as st

import utils.logs as logs

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from llama_index.core.node_parser import SentenceSplitter

from llama_index.vector_stores.faiss import FaissVectorStore

from faiss import IndexFlatL2

# This is not used but required by llama-index and must be set FIRST
# os.environ["OPENAI_API_KEY"] = "sk-abc123"


from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
)


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
    
    logs.log.info(f"Setting up embedding model: {model}")
    
    try:
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=model,
            device=device,
        )
        logs.log.info(f"Embedding model created successfully")        
        logs.log.info(f"Embedding model is {Settings.embed_model}")
        return Settings.embed_model
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
    
    logs.log.info(f"Document list is {_documents[0]}")
    
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
        
        index.storage_context.persist(persist_dir=os.getcwd() + "/vector_db")   
        logs.log.info("Index created from loaded documents successfully")
    
    except Exception as err:
        logs.log.error(f"Index creation failed with user defined chunk size and chunk overlap: {err}")
        
        try : 
            index = VectorStoreIndex.from_documents(
            documents=_documents, show_progress=True,
            )
            logs.log.info("Index created from loaded documents successfully")
            index.storage_context.persist(persist_dir=os.getcwd() + "/vector_db") 

        except Exception as err:
            logs.log.error(f"Index creation failed with default chunk size and chunk overlap: {err}")
            raise Exception(f"Index creation failed with default chunk size and chunk overlap: {err}")

    
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
        
    try:
        # Vector index generated from set of documents : 
        index = create_index(_documents)
        # Save the vector index to disk
        
        query_engine = index.as_query_engine(
            similarity_top_k=st.session_state["top_k"],
            response_mode=st.session_state["chat_mode"],
            streaming=True,
        )

        # Assigned query engine object to session state. 
        st.session_state["query_engine"]=query_engine

        logs.log.info("Query Engine created successfully")

        return query_engine
    
    except Exception as e:
        logs.log.error(f"Error when creating Query Engine: {e}")
        raise Exception(f"Error when creating Query Engine: {e}")


###################################
#
# Create FAISS Index : Vector Store with optimized search using ANNs , Complexity O(log(n))
#
###################################

def create_faiss_index(_documents,dimensions):
    
    try:
        # Define FAISS storage path
        
        faiss_db_path = os.path.join(os.getcwd(), "faiss_db")
        if not os.path.exists(faiss_db_path):
            os.makedirs(faiss_db_path)
        
        # Create or load FAISS vector store
        try : 
            # check if faiss_db_path exists :
            faiss_store = FaissVectorStore.from_persist_dir(faiss_db_path)
        except Exception as e:
            
            # Get the dimension of the embedding model
            faiss_index = IndexFlatL2(dimensions)
            faiss_store = FaissVectorStore(faiss_index=faiss_index)

        # Create storage context with FAISS
        storage_context = StorageContext.from_defaults(vector_store=faiss_store, persist_dir=faiss_db_path)

        # Create index using FAISS as vector store
        try : 
            index = VectorStoreIndex.from_documents(
                documents=_documents, 
                storage_context=storage_context,  # Store in FAISS
                show_progress=True,
                transformations=[
                    SentenceSplitter(chunk_size=st.session_state["chunk_size"],
                                     chunk_overlap=st.session_state["chunk_overlap"],
                                     separator=".",
                                     paragraph_separator="\n\n")
                ],
            )
        except Exception as e:
            try : 
                index = VectorStoreIndex.from_documents(
                    documents=_documents, 
                    storage_context=storage_context,  # Store in FAISS
                    show_progress=True,
                )  
            except Exception as e:
                raise Exception(f"Error creating index with FAISS: {e}")
            
        # Persist FAISS index , save vector db to disk. 
        faiss_store.persist(faiss_db_path)
        
        logs.log.info("FAISS index created and stored successfully")
        return index
    
    except Exception as err:
        logs.log.error(f"Index creation failed: {err}")
        raise Exception(f"Index creation failed: {err}")  