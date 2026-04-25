# 🚀 Contextual Codebase AI

An intelligent system that analyzes any GitHub repository and answers questions about its codebase using AI, embeddings, and backend services.

---

## 🧠 Overview

Contextual Codebase AI allows users to:

* 📂 Input a GitHub repository
* ⚙️ Automatically index the codebase
* 🤖 Ask questions about the project
* 📊 Get structured, AI-generated explanations

This project demonstrates how AI can be integrated with backend systems to understand and reason about large codebases.

---

## 🏗️ Architecture

```
Frontend (React)
        ↓
Backend (Node.js + Express)
        ↓
AI Service (Python + FastAPI)
        ↓
Embeddings + LLM
        ↓
MongoDB Atlas


- **Agentic Loop**: Query → RAG retrieval → Cosine similarity confidence scoring → Critic decision → Retry if confidence < 0.5 (max 3 iterations)
- **Isolation**: Each project's FAISS index is namespaced by `project_id` — no cross-user data leakage
- **Security**: GitHub URL validation on all index requests; CORS restricted to frontend origin

```

---

## ⚙️ Tech Stack

### Frontend

* React (Vite)
* Axios

### Backend

* Node.js
* Express.js
* MongoDB Atlas

### AI Service

* FastAPI
* Sentence Transformers (Embeddings)
* OpenRouter (LLM)

### DevOps

* Docker & Docker Compose

---

## 📦 Features

* 🔍 GitHub repository indexing
* 🧩 Code chunking & embeddings
* 💬 Natural language query system
* ⚡ Real-time API communication
* 🐳 Fully dockerized setup

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/ayushks404/contextual_codebase.git
```

---

### 2. Setup Environment Variables

#### Backend (`/backend/.env`)

```
MONGO_URI=your_mongodb_atlas_uri
JWT_SECRET=your_secret
AI_SERVICE_URL=http://ai_service:8000
```

---

#### AI Service (`/ai_service/.env`)

```
OPENROUTER_API_KEY=your_key
SUPABASE_URL=your_url   # optional
SUPABASE_KEY=your_key   # optional
```

---

### 3. Run with Docker

```bash
docker-compose up --build
```

---

### 4. Access the Application

| Service  | URL                   |
| -------- | --------------------- |
| Frontend | http://localhost:5173 |
| Backend  | http://localhost:5000 |
| AI API   | http://localhost:8000 |

---

## 🧪 API Endpoints

### 🔹 Index Repository

```http
POST /index-repo
```

**Request Body:**

```json
{
  "repo_url": "https://github.com/user/repo"
}
```

---

### 🔹 Query Codebase

```http
POST /query
```

**Request Body:**

```json
{
  "project_id": "project_id",
  "question": "Explain authentication flow"
}
```

---

## ⚠️ Known Limitations

* Large repositories may take time to index
* External APIs (LLM) may introduce latency
* Requires valid API keys

---

## 🔮 Future Improvements

* Multi-agent system using LangGraph
* Replace external vector DB with FAISS
* Code dependency graph visualization
* Performance optimizations

---

## 🧠 Key Learnings

* Microservices architecture
* AI integration with backend systems
* Embeddings and vector search
* Docker-based development workflow

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 📜 License

MIT License

---

## 👨‍💻 Author

Ayush Kumar Sharma
