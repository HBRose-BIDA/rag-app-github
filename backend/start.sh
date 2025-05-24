#!/bin/bash

# Optional: Start Ollama if it's not already running
# ollama serve &

# Load documents into FAISS
python3 -c "import rag; rag.load_documents()"

# Start FastAPI
uvicorn app:app --host 0.0.0.0 --port 80
