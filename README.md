# RAG App (Retrieval-Augmented Generation)

This is a document-grounded question-answering backend application built with FastAPI and OpenAI's GPT API. It uses embedded document chunks to answer questions with factual accuracy — no hallucinations — and provides grounded responses sourced from real documents.

## 📌 Features

* 🔍 Query over real documents (PDF, DOCX, PPTX, XLSX, SQL, Python, etc.)
* 📄 Returns grounded answers with document context
* 🚀 FastAPI backend served by Uvicorn
* 💡 Clean static UI (optional `index.html`)
* 🧠 Uses OpenAI embeddings + GPT for generation

## 📂 Project Structure

```
rag-app/
├── rag.py              # Main FastAPI app with `/ask` endpoint
├── start.sh            # Startup script for systemd or manual run
├── requirements.txt    # Python dependencies
├── index.html          # Static frontend (optional)
├── deploy/             # Deployment configs (Nginx, systemd, etc.)
│   └── rag-app.conf    # Nginx reverse proxy config (optional)
└── .env.example        # Sample environment config (excluded in real deploy)
```

## ⚙️ Requirements

* Python 3.10+
* OpenAI API Key
* Uvicorn / FastAPI
* (Optional) Nginx and systemd for production hosting

## 🚀 Running the App

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set environment variables

Create a `.env` file using `.env.example` as a guide:

```env
OPENAI_API_KEY=your-key-here
MODEL_NAME=gpt-4
```

### 3. Start the server

```bash
bash start.sh
```

Or manually:

```bash
python rag.py --serve
```

## 🌐 Deployment (Optional)

You can use `Nginx` + `systemd` to run this as a background service.

Example:

* Nginx config: `deploy/rag-app.conf`
* Systemd unit: `rag-app.service` (optional)

## 🧪 Sample Usage

Send a POST request to the `/ask` endpoint:

```bash
curl -X POST http://<your-server>/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What experience does the candidate have with SQL?"}'
```

The server returns:

```json
{
  "answer": "The candidate has used SQL to join and query customer and transaction tables in multiple academic and professional settings...",
  "sources": ["doc1.docx", "project_summary.pdf"]
}
```

## 🛡️ Notes

* This app is designed for read-only usage over pre-approved documents.
* All documents should be embedded in advance and stored securely.
* Do **not** upload documents containing sensitive or personal data to public repositories.

## 🗾️ License

MIT License – feel free to adapt and reuse with credit.

## 😋 Author

Rudy Rose – created for a recruiter-facing RAG prototype.
