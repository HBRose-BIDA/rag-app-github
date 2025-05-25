
# RAG App – Document-Based Question Answering

This project delivers a secure, low-cost, document-grounded Q&A system using:

* 🧠 OpenAI GPT-3.5
* 🔍 FAISS vector search
* 📄 Document embedding via sentence-transformers
* 🌐 FastAPI backend hosted on Hetzner
* 🖼️ Static frontend hosted via GitHub Pages

---

## ✅ Live Demo

* **Frontend (GitHub Pages):**

  [https://hbrose-bida.github.io/rag-app-github/](https://hbrose-bida.github.io/rag-app-github/)
* **Backend API (Hetzner):**

  [https://hbr-bida.duckdns.org/query](https://hbr-bida.duckdns.org/query)

---

## 🛍️ How It Works

1. Documents (`.pdf`, `.docx`, `.pptx`, `.xlsx`) are uploaded to a private server
2. On app startup, documents are embedded and indexed using FAISS
3. User submits a natural-language question via the frontend
4. The backend searches for top matching chunks
5. The selected chunks are sent to OpenAI GPT-3.5 for answer generation
6. The answer is returned to the frontend in real time

---

## 📁 Repo Structure

```plaintext
rag-app-github/
├── docs/           # GitHub Pages frontend
│   └── index.html
│
├── backend/        # FastAPI backend (runs on Hetzner)
│   ├── rag.py
│   ├── start.sh
│   ├── requirements.txt
│   └── documents/  # Not committed; ignored via .gitignore
│
├── .gitignore
└── README.md
```

---

## 🚀 Backend Setup (on Hetzner VPS)

```bash
cd backend
pip3 install -r requirements.txt
systemctl start rag-app
```

* App listens on `localhost:8000`
* NGINX proxies traffic from `https://hbr-bida.duckdns.org/`
* OpenAI API key is set via systemd environment (not in code)

---

## 🔐 API Key Management

In `/etc/systemd/system/rag-app.service`, include:

```ini
Environment=OPENAI_API_KEY=sk-...
```

Then reload and restart:

```bash
systemctl daemon-reexec
systemctl daemon-reload
systemctl restart rag-app
```

---

## 🛡️ HTTPS + Domain

* NGINX reverse proxy on port 443 (HTTPS)
* Certbot via Let's Encrypt
* Uses DuckDNS subdomain: `hbr-bida.duckdns.org`

---

## 🥮 Test It

Ask:

```
What is one element of ethics?
```

You’ll receive a real, document-grounded OpenAI response.

---

## 🛠️ Technologies Used

* FastAPI + Uvicorn
* FAISS (vector similarity search)
* SentenceTransformers (`all-MiniLM-L6-v2`)
* OpenAI GPT-3.5 API
* NGINX + Certbot (HTTPS)
* GitHub Pages (frontend)

---

## 📄 License

This project is for educational or internal demonstration purposes. MIT-style license optional.
