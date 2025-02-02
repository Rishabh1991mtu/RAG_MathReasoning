import streamlit as st
import utils.logs as logs

from utils.ollama_utility import chat, context_chat
import utils.llama_index as llama_index

def chatbox():
    if prompt := st.chat_input("How can I help?"):
        # Prevent submission if Ollama endpoint is not set
        if not st.session_state["query_engine"]:
            st.warning("Please confirm settings and upload files before proceeding.")
            st.stop()

        # Add the user input to messages state
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        logs.log.info(f"prompt is {prompt}")
        
        # Generate llama-index stream with user input
        with st.chat_message("assistant "):
            with st.spinner("Processing..."):
                response = st.write_stream(
                    # chat(
                    #     prompt=prompt
                    # )
                    context_chat(
                        prompt=prompt, query_engine=st.session_state["query_engine"]
                    )
                )  
                
        # Find the embeddings for the retrieved chunks : 
        # Create an embedding from the prompt using Settings.embed_model      
        
        retrieved_nodes = st.session_state["query_engine"].retrieve(prompt) 
        logs.log.info(f"retrieved_nodes total is {len(retrieved_nodes)}")
        
        # Extract filename and scores from retrieved chunks : 
        
        file_name = [node.metadata.get('file_name', 'N/A') for node in retrieved_nodes]
        scores = [round(node.score, 3) for node in retrieved_nodes]

        # Add the final response to messages state
        st.session_state["messages"].append({"role": "assistant", "content": response})
        
        citations = "Citations:<br>"       

        # Display document from which data is retrieved along with scores
        for index, (files, score) in enumerate(zip(file_name, scores)):
            citations += (f"Chunk {index + 1}: (Similarity Score: {score}) Filename : {files}<br>")
        
        with st.chat_message("assistant"):
            st.markdown(citations, unsafe_allow_html=True)

        # Add the final response to messages state
        st.session_state["messages"].append({"role": "assistant", "content": response})

        # Display the final response
        #logs.log.info(f"response is {response}")

        
        