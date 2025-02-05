# Math RAG implementation :

This application is specifically fine-tuned to handle math-related questions. Users can ask math-related questions from the documents, and the bot is designed to understand and process math expressions, providing accurate answers.

![Math RAG Bot](docs/images/math_rag_bot.png)

### Key Features

- **Math Expression Understanding**: The bot is fine-tuned to understand and interpret complex math expressions.
- **Vector index**: Documents loaded will be processed as text and embeddings save in vectorindex stored in folder vector_db
- **Document-Based Question Answering**: Users can ask questions based on the content of the ingested documents.
- **Math Solutions**: The bot provides provides solutions to math problems, leveraging its understanding of mathematical concepts in a step by step manner.
- **Ground Truth**: The app also shares the document names and vector similarity score with the retrieved chunks. 
- **Latex based formattting**: The LLM is instructed to generate resppnse in LateX notation which is rendered in UI.  

## Usage

1. **Ingest Documents**: Upload your math-related documents to the application.
2. **Ask Questions**: Use the chat interface to ask math-related questions.
3. **Get Answers**: Receive accurate answers with properly formatted math expressions.

Setup and usage instructions : 

- [Setup & Deploy the App](docs/setup.md)
- [Using Local RAG](docs/usage.md)
- [RAG Pipeline](docs/pipeline.md)
- [API Endoints](docs/endpoint.md)

Troubleshooting : 
- [Troubleshooting](docs/troubleshooting.md)
- [Documents](docs/troubleshooting.md)