import time

import streamlit as st
import threading
import requests
from components.chatbox import chatbox
from components.header import set_page_header
from components.sidebar import sidebar

from components.page_config import set_page_config
from components.page_state import set_initial_state

def start_frontend_app():
    
    ### Setup Initial State
    set_initial_state()

    ### Page Setup
    set_page_config()
    set_page_header()

    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])
        
    ### Sidebar
    sidebar()

    ### Chat Box
    chatbox()

def run():
    
    # Start the Fast API for backend
    #run_fastapi()
    
    # Start the Streamlit app
    start_frontend_app()   

if __name__ == "__main__":
    run()
    
# script : Unicorn server start. 