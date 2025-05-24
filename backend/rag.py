import os
import glob
import faiss
import numpy as np
import pandas as pd
import PyPDF2
import docx
from pptx import Presentation
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# --- Initialize FastAPI ---
app = FastAPI()

# --- Enable CORS for frontend access ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Serve static frontend (index.html) ---
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# --- OpenAI client (secure) ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Embedding Model ---
model = SentenceTransformer("all-MiniLM-L6-v2")
chunks = []
chunk_texts = []
index = None

# ----------- Document Parsing -----------

def extract_text(file):
    if file.endswith(".pdf"):
        with open(file, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif file.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    elif file.endswith(".pptx"):
        prs = Presentation(file)
        return "\n".join(shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, "text"))
    elif file.endswith(".xlsx"):
        return "\n".join([sheet.to_string() for _, sheet in pd.read_excel(file, sheet_name=None).items()])
    return ""

def split_text(text, max_length=1500):
    sentences = text.split(".")
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + "."
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + "."
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def embed_texts(texts):
    return model.encode(texts, convert_to_numpy=True)

def load_documents():
    global chunks, chunk_texts
    for file in glob.glob("documents/*"):
        if file.endswith((".pdf", ".docx", ".pptx", ".xlsx")):
            text = extract_text(file)
            if text:
                for chunk in split_text(text):
                    chunks.append(chunk)
                    chunk_texts.append(chunk)

# ----------- FAISS Indexing -----------

def build_index():
    global index
    if not chunks:
        return
    embeddings = embed_texts(chunks).astype("float32")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

# ----------- OpenAI Completion -----------

def ask_openai(question, context):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Use the provided context to answer the question as clearly as possible."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def get_answer(question):
    if not index:
        return "Index not ready."
    question_embedding = embed_texts([question])
    D, I = index.search(question_embedding, 3)
    context_chunks = [chunk_texts[i] for i in I[0] if i < len(chunk_texts)]
    context = "\n\n".join(context_chunks)
    return ask_openai(question, context)

# ----------- FastAPI Routes -----------

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query(req: QueryRequest):
    answer = get_answer(req.question)
    return {"answer": answer}

@app.get("/status")
async def root():
    return {"message": "RAG backend with OpenAI is live"}

# ----------- Startup Hook -----------

@app.on_event("startup")
def startup():
    load_documents()
    build_index()
