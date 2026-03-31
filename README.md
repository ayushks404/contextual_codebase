Contextual Codebase Analysis (CCA)
Contextual Codebase Analysis is a full-stack Retrieval-Augmented Generation (RAG) platform that empowers developers to understand and query complex codebases. By securely cloning, chunking, and indexing Git repositories, the system allows users to ask natural language questions and receive accurate, context-aware answers grounded in the actual source code.

🚀 Features
Automated Repository Processing: Clones remote repositories, intelligently chunks source code files, and processes them for AI analysis.

RAG-Powered Code Search: Uses localized text embeddings and FAISS vector search to retrieve relevant code snippets based on user queries.

Context-Aware AI Chat: Integrates with OpenRouter LLMs to explain code, debug issues, and document architecture using the retrieved repository context.

User & Project Management: Secure JWT-based authentication to manage individual workspaces, project metadata, and query histories.

Containerized Microservices: Fully dockerized architecture orchestrating a Node.js backend, a Python AI service, a React frontend, and a local embedding API.

🛠️ Tech Stack
Frontend
React.js (via Vite)

Tailwind CSS (for responsive styling)

Backend (Orchestrator)
Node.js & Express.js (API routing & Authentication)

MongoDB & Mongoose (User, Project, and Chat History storage)

JWT (Secure session management)

AI Service (RAG Engine)
Python & FastAPI (High-performance ML processing)

FAISS (Local vector similarity search)

Supabase (Cloud storage for persistent vector indices and metadata)

Stapi / Substratus AI (Local embedding generation via all-MiniLM-L6-v2)

OpenRouter API (LLM inference)

📂 Project Structure
Plaintext
contextual_codebase/
├── frontend/             # React + Vite web application
│   ├── src/pages/        # Dashboard, Login, Register, Query views
│   └── src/components/   # Reusable UI components (Navbar, MessageBubble)
├── backend/              # Node.js/Express API server
│   ├── src/models/       # Mongoose schemas (User, Project, Query)
│   ├── src/routes/       # API endpoints (/auth, /project, /query)
│   └── src/controllers/  # Business logic
├── ai_service/           # Python FastAPI application
│   ├── services/         # RAG pipeline (chunker, embeddings, rag_engine)
│   └── app.py            # FastAPI endpoints (/index-repo, /query, /cleanup)
└── docker-compose.yml    # Multi-container orchestration
📋 Prerequisites
Ensure you have the following installed on your system before proceeding:

Docker and Docker Compose

Git

API Keys for:

OpenRouter (For LLM responses)

Supabase (For storing FAISS index data)

Hugging Face (Optional, depending on Stapi usage)

⚙️ Environment Configuration
Create a .env file in the root directory. The docker-compose.yml relies on these variables to inject configuration into the respective containers.

Code snippet
# Backend / Database
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=your_super_secret_jwt_key

# Supabase Storage (AI Service)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_key
SUPABASE_BUCKET=your_storage_bucket_name

# AI Models (AI Service / Stapi)
OPENROUTER_API_KEY=your_openrouter_api_key
HF_TOKEN=your_huggingface_token
🚀 Running the Application (Docker)
The easiest way to run the entire stack is using Docker Compose. It will automatically build the frontend, backend, AI service, and pull the Stapi embeddings image.

Build and start the containers:

Bash
docker-compose up --build
Access the Application:

Frontend UI: http://localhost:5173

Backend API: http://localhost:5000

AI Service Docs: http://localhost:8000/docs (Swagger UI)

Stapi (Embeddings): http://localhost:8081

To stop the application:

Bash
docker-compose down
💻 Running Locally (Without Docker)
If you prefer to run the services individually for development:

1. Backend
Bash
cd backend
npm install
# Ensure you have a local MongoDB running or update MONGO_URI in backend/.env
npm run dev
2. AI Service
Bash
cd ai_service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
# Ensure you start a local embedding model or mock the stapi endpoint
uvicorn app:app --reload --port 8000
3. Frontend
Bash
cd frontend
npm install
npm run dev
🛡️ Core Architecture Flow
Indexing (/api/project/create ➔ AI Service /index-repo): When a user submits a repository URL, the backend registers the project and triggers the FastAPI service. The AI service clones the repo, reads the files, chunks the code, generates vector embeddings using the local Stapi container, and saves the FAISS index to Supabase.

Querying (/api/query ➔ AI Service /query): Users ask questions via the React frontend. The backend logs the query and forwards it to the AI service. The AI service converts the question to an embedding, searches the FAISS index for the top-K relevant code chunks, and constructs a detailed prompt for the OpenRouter LLM to generate a codebase-specific answer.
