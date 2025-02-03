import streamlit as st
import utils.logs as logs

from utils.ollama_utility import chat, context_chat
import utils.llama_index as llama_index

import re

def render_response(response):
    """
    Function to render a response containing text and LaTeX expressions in Streamlit.

    Args:
        response (str): The response string containing text and LaTeX expressions.
    """
    # Regular expression to extract LaTeX expressions inside square brackets
    latex_pattern = r"\[([^\]]+)\]"

    # Find all LaTeX expressions
    latex_expressions = re.findall(latex_pattern, response)

    # Split response into text and LaTeX parts
    text_parts = re.split(latex_pattern, response)
    logs.log.info(f"text_parts is {text_parts}")

    st.title("Auto-Formatted Markdown and LaTeX in Streamlit")

    # Iterate through text and LaTeX expressions
    for part in text_parts:
        if part.endswith("\\"):
            part = part[:-1]  # Remove the trailing backslash
        if part in latex_expressions:
            st.latex(part)  # Render LaTeX expression
            #st.latex(r"\lim_{x \to 0} \frac{\sin(x)}{x}")
        else:
            st.markdown(part)  # Render text explanation

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
        
        render_response(response)
                
        # Retrieve the nodes from the query engine based on the user input.       
        retrieved_nodes = st.session_state["query_engine"].retrieve(prompt) 
        logs.log.info(f"retrieved_nodes total is {len(retrieved_nodes)}")
        
        # Extract filename and scores from retrieved chunks and create a dictionary for unique file names
        file_scores_dict = {}
        for node in retrieved_nodes:
            file_name = node.metadata.get('file_name', 'N/A')
            score = round(node.score, 3)
            if file_name not in file_scores_dict:
                file_scores_dict[file_name] = []
                file_scores_dict[file_name].append(score)
            else: 
                file_scores_dict[file_name].append(score)
        
        citations = "Citations:<br>"       

        # Display document from which data is retrieved along with scores
        chunk_index = 1
        file_index = 1
        for file_name, scores in file_scores_dict.items():
            citations += f"<h4>{file_index}. Filename: {file_name}<h4><br>"
            citations += "<table><tr><th>Chunk</th><th>Similarity Score</th></tr>"
            file_index += 1
            for score in scores:
                citations += f"<tr><td>{chunk_index}</td><td>{score}</td></tr>"
                chunk_index += 1
            citations += "</table><br>"

        # Send Citations to chat.
        with st.chat_message("assistant"):
            st.markdown(citations, unsafe_allow_html=True)

        # Add the final response to messages state
        st.session_state["messages"].append({"role": "assistant", "content": response})

        # Display the final response
        #logs.log.info(f"response is {response}")
        
        

        
        