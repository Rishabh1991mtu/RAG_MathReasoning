import os
import json
from llama_index import SimpleDirectoryReader
from utils.llama_index import create_faiss_index  # Your function
import utils.logs as logs # Ensure logging works

# Define paths
DOCS_DIR = os.getcwd() + "math_documents"
INDEXED_FILES_PATH = "indexed_files.json"

# Load previously indexed files
if os.path.exists(INDEXED_FILES_PATH):
    with open(INDEXED_FILES_PATH, "r") as f:
        indexed_files = json.load(f)
else:
    indexed_files = {}

# Get all files in the directory
all_files = {f: os.path.getmtime(os.path.join(DOCS_DIR, f)) for f in os.listdir(DOCS_DIR)}

# Find new or updated files
new_files = [f for f in all_files if f not in indexed_files or all_files[f] > indexed_files[f]]

if not new_files:
    print("✅ No new or modified documents. FAISS update skipped.")
else:
    print(f"🚀 Found {len(new_files)} new/updated documents. Updating FAISS index...")

    # Load only new documents
    new_documents = SimpleDirectoryReader(input_files=[os.path.join(DOCS_DIR, f) for f in new_files]).load_data()

    # Update FAISS index
    try:
        create_faiss_index(new_documents)
        print("✅ FAISS index updated successfully!")

        # Update indexed_files.json with newly indexed files
        indexed_files.update(all_files)
        with open(INDEXED_FILES_PATH, "w") as f:
            json.dump(indexed_files, f, indent=4)
    except Exception as e:
        print(f"❌ Error updating FAISS index: {e}")
