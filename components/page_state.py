import streamlit as st

import utils.logs as logs

from utils.ollama_utility import get_models

def set_initial_state():

    ###########
    # General #
    ###########

    if "sidebar_state" not in st.session_state:
        st.session_state["sidebar_state"] = "expanded"

    if "ollama_endpoint" not in st.session_state:
        st.session_state["ollama_endpoint"] = "http://localhost:11434"

    if "embedding_model" not in st.session_state:
        st.session_state["embedding_model"] = "BAAI/bge-large-en-v1.5"

    if "ollama_models" not in st.session_state:
        try:
            models = get_models()
            st.session_state["ollama_models"] = models
        except Exception:
            st.session_state["ollama_models"] = []
            pass

    if "selected_model" not in st.session_state:
        try:
            if "llama3:8b" in st.session_state["ollama_models"]:
                st.session_state["selected_model"] = (
                    "llama3:8b"  # Default to llama3:8b on initial load
                )
            elif "llama2:7b" in st.session_state["ollama_models"]:
                st.session_state["selected_model"] = (
                    "llama2:7b"  # Default to llama2:7b on initial load
                )
            else:
                st.session_state["selected_model"] = st.session_state["ollama_models"][
                    0
                ]  # If llama2:7b is not present, select the first model available
        except Exception:
            st.session_state["selected_model"] = None
            pass

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "Welcome to Local RAG! To begin, please either import some files or ingest a GitHub repo. Once you've completed those steps, we can continue the conversation and explore how I can assist you further.",
            }
        ]

    ################################
    #  Files, Documents & Websites #
    ################################

    if "file_list" not in st.session_state:
        st.session_state["file_list"] = []

    if "github_repo" not in st.session_state:
        st.session_state["github_repo"] = None

    if "websites" not in st.session_state:
        st.session_state["websites"] = []

    ###############
    # Llama-Index #
    ###############

    if "llm" not in st.session_state:
        st.session_state["llm"] = None

    if "documents" not in st.session_state:
        st.session_state["documents"] = None

    if "query_engine" not in st.session_state:
        st.session_state["query_engine"] = None

    if "chat_mode" not in st.session_state:
        st.session_state["chat_mode"] = "compact"

    #####################
    # Advanced Settings #
    #####################

    if "advanced" not in st.session_state:
        st.session_state["advanced"] = False

    # RAG Math Enhacement 1 : Applied chain of thought prompts and few shot propmts to improve the response quality.
    # Specifically mentioned to return response provide the response in LaTeX format.
            
    if "system_prompt" not in st.session_state:
        st.session_state["system_prompt"] = (
            '''
                You are AI Math Assistant. The student will ask math questions using  
                natural language, symbolic expressions and LaTeX notations formats to represent mathematical equations. You need to follow the steps below strictly:

                    1. Read the question carefully and take your time to understand it.
                    2. Break down the question into smaller parts and identify the key concepts needed to solve the problem.
                    3. Utilize only the given textbooks, papers, and references to guide your response. Do not use external knowledge beyond the retrieved documents.
                    4. Once you have understood the question and the relevant concepts, provide a step-by-step solution to the student.
                    5. Accurately interpret and respond to questions in standard text and LaTeX notation.
                    6. Before displaying an answer, cross-check the response against the retrieved documents. If an answer is not supported by the provided context, state that the answer is not available.
                    7. Use self-consistency prompting by solving the problem in multiple ways and comparing results to verify correctness.

                    Instructions to follow while answering the question:

                    1. Start with: "Hello, I am your AI Math Assistant."
                    2. Return the response in LaTeX format, using \[ \] for block mode and \( \) for inline mode.

                    Example format:

                    Question 1: What is the Laplace transform of \( e^{-at} \)?

                    Answer:
                    The Laplace transform of \( e^{-at} \) is given by:

                    \[
                    \mathcal{L}\{e^{-at}\} = \int_{0}^{\infty} e^{-at} e^{-st} \, dt = \int_{0}^{\infty} e^{-(s+a)t} \, dt
                    \]

                    Evaluating the integral:

                    \[
                    \mathcal{L}\{e^{-at}\} = \left[ \frac{e^{-(s+a)t}}{-(s+a)} \right]_{0}^{\infty} = \frac{1}{s+a} \quad \text{for} \quad \text{Re}(s) > -a
                    \]

                    So, the Laplace transform of \( e^{-at} \) is \( \frac{1}{s+a} \).

                    ---

                    Question 2: How to solve the quadratic equation \(2x^2 + 3x - 5 = 0\)?

                    Answer:
                    To solve the quadratic equation \(2x^2 + 3x - 5 = 0\), we use the quadratic formula:

                    \[
                    x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
                    \]

                    Given \( a = 2 \), \( b = 3 \), and \( c = -5 \), we substitute:

                    \[
                    x = \frac{-3 \pm \sqrt{3^2 - 4(2)(-5)}}{2(2)}
                    \]

                    \[
                    x = \frac{-3 \pm \sqrt{9 + 40}}{4}
                    \]

                    \[
                    x = \frac{-3 \pm \sqrt{49}}{4}
                    \]

                    \[
                    x = \frac{-3 \pm 7}{4}
                    \]

                    Thus, the solutions are:

                    \[
                    x = \frac{-3 + 7}{4} = 1 \quad \text{or} \quad x = \frac{-3 - 7}{4} = -2.5
                    \]

                    ---

                    Question 3: What is the area of a circle with a radius of 5 cm?

                    Answer:
                    The documents provided do not contain the formula for the area of a circle. I am unable to provide the exact value of the area of a circle with a radius of 5 cm.

                    Question 4: What is the capital of France?

                    Answer:
                    This is not a math-related question, so no mathematical solution is required.
                    I have been instructed to provide only math-related answers. Please ask a math-related question.

            '''
        )

    if "top_k" not in st.session_state:
        st.session_state["top_k"] = 3

    if "embedding_model" not in st.session_state:
        st.session_state["embedding_model"] = None

    if "other_embedding_model" not in st.session_state:
        st.session_state["other_embedding_model"] = None

    if "chunk_size" not in st.session_state:
        st.session_state["chunk_size"] = 1024

    if "chunk_overlap" not in st.session_state:
        st.session_state["chunk_overlap"] = 200
