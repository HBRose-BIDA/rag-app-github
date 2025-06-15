import os
import sys
import uvicorn
import openai
import faiss
import numpy as np
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from docx import Document

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load and process documents
def load_documents(directory):
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(".docx"):
            path = os.path.join(directory, filename)
            doc = Document(path)
            text = "\n".join(p.text for p in doc.paragraphs)
            documents.append((filename, text))
    return documents

# Embed using OpenAI
def embed_documents(texts):
    return [openai.Embedding.create(input=[text], model="text-embedding-ada-002")["data"][0]["embedding"] for text in texts]

# Build FAISS index
def build_index(embeddings):
    if not embeddings:
        print("❌ No embeddings found.")
        sys.exit(1)
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))
    return index

# Load, embed, and index
print("Loading documents...")
docs = load_documents("./docs")
print(f"Loaded {len(docs)} documents")

if not docs:
    print("❌ No documents found. Exiting.")
    sys.exit(1)

print("Embedding documents...")
texts = [d[1] for d in docs]
embeddings = embed_documents(texts)

print("Building FAISS index...")
index = build_index(embeddings)

# Define /ask route
@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    question = data.get("question", "")
    if not question:
        return {"answer": "No question provided."}

    q_embedding = openai.Embedding.create(input=[question], model="text-embedding-ada-002")["data"][0]["embedding"]
    D, I = index.search(np.array([q_embedding]).astype("float32"), k=3)
    context = "\n\n".join([docs[i][1] for i in I[0] if i < len(docs)])

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Use the following documents:\n\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,
    )

    return {"answer": response.choices[0].message["content"].strip()}

# Serve if requested
if __name__ == "__main__":
    if "--serve" in sys.argv:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print("Loaded documents without starting server.")
