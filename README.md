# RAG App: Public Document QA System

This project includes a FastAPI-based backend hosted on Hetzner and a browser-accessible frontend hosted via GitHub Pages.

## 🧠 What It Does

- Accepts natural-language questions
- Searches a local set of documents
- Uses OpenAI GPT-3.5 to generate context-based answers

## 📁 Repo Structure

- `docs/` – GitHub Pages frontend (`index.html`)
- `backend/` – FastAPI app deployed to Hetzner VPS

## 🚀 How to Use

1. Visit the frontend: https://your-username.github.io/your-repo/
2. Ask a question
3. The backend (running at `http://5.161.224.212`) returns an answer

## 🔐 API Key

- The OpenAI key is stored securely in Hetzner via `systemd`
- Not included in this repo

## 🛠 Setup (Hetzner VPS)

```bash
cd backend
pip3 install -r requirements.txt
systemctl start rag-app
```
