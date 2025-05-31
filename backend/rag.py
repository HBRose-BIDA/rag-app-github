import os
import openai
import faiss
import pickle
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PyPDF2 import PdfReader
from pptx import Presentation
from docx import Document
from sentence_transformers import SentenceTransformer
from typing import List

# ----------------------- CONFIG -----------------------
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# ----------------------- FASTAPI -----------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

# ----------------------- UTILS -----------------------
def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def load_documents(directory: str):
    docs = []
    sources = []
    for root, _, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            try:
                if ext == ".pdf":
                    reader = PdfReader(path)
                    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
                elif ext == ".docx":
                    doc = Document(path)
                    text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
                elif ext == ".pptx":
                    prs = Presentation(path)
                    text = "\n".join(shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, "text"))
                elif ext == ".txt":
                    with open(path, "r", encoding="utf-8") as f:
                        text = f.read()
                elif ext == ".xlsx":
                    import openpyxl
                    wb = openpyxl.load_workbook(path, data_only=True)
                    text = "\n".join(str(cell.value) for sheet in wb.worksheets for row in sheet.iter_rows() for cell in row if cell.value)
                else:
                    continue
                for chunk in chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP):
                    docs.append(chunk)
                    sources.append(file)
            except Exception as e:
                print(f"Failed to process {path}: {e}")
    return docs, sources

def build_faiss_index(embeddings):
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def query_rag(question, index, chunks, sources, model, api_key):
    question_embedding = model.encode([question])
    scores, indices = index.search(question_embedding, k=5)
    retrieved = [chunks[i] for i in indices[0]]
    context = "\n\n".join(retrieved)

    openai.api_key = api_key
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ]
    )
    return response.choices[0].message.content

# ----------------------- STARTUP -----------------------
print("Loading embedding model...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
print("Loading documents...")
docs, doc_sources = load_documents("docs")
print(f"Loaded {len(docs)} documents")

print("Embedding documents...")
doc_embeddings = embedding_model.encode(docs, show_progress_bar=True)
print("Building FAISS index...")
index = build_faiss_index(doc_embeddings)

# ----------------------- ENDPOINT -----------------------
@app.post("/ask")
async def ask(q: Question, request: Request):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"error": "Missing OpenAI API Key"}
    try:
        result = query_rag(q.question, index, docs, doc_sources, embedding_model, api_key)
        return {"answer": result}
    except Exception as e:
        return {"error": str(e)}

# ----------------------- CLI ENTRY -----------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RAG Loader")
    parser.add_argument("--serve", action="store_true", help="Start API server")
    args = parser.parse_args()

    if not args.serve:
        print("Loaded documents without starting server.")
