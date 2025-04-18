# RAG Chatbot: Document-Enhanced AI Assistant


![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.44.x-FF4B4B)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.x-009688)
![Langchain](https://img.shields.io/badge/Langchain-latest-2496ED)

A powerful Retrieval-Augmented Generation (RAG) system that enhances your AI interactions with the knowledge present in your documents.

## 📋 Overview

This project implements a sophisticated RAG architecture with:

- **Streamlit frontend** for intuitive user interactions
- **FastAPI backend** for robust API endpoints
- **Langchain** for advanced LLM orchestration
- **Qdrant** vector database for efficient semantic retrieval
- **OpenAI** language models for high-quality responses

RAG enhances traditional AI chat interfaces by retrieving relevant context from your documents before generating responses, resulting in more accurate, informative, and contextually relevant answers.


## ✨ Features

### Document Management
- **Multi-format Support:** Upload PDF, DOCX, and HTML documents
- **Document Library:** Maintain and browse your knowledge base
- **Selective Deletion:** Remove documents when no longer needed

### AI Chat Experience
- **Contextual Understanding:** Get answers informed by your documents  
- **Model Selection:** Choose between OpenAI models (gpt-4o, gpt-4o-mini)
- **Session Persistence:** Continue conversations with context
- **Query Refinement:** Automatic enhancement of ambiguous queries

### Technical Features
- **Vector Embeddings:** Semantic understanding of document content
- **Efficient Chunking:** Dynamic text segmentation for optimal retrieval
- **Asynchronous Processing:** Fast, non-blocking operations
- **Session Management:** Persistent user sessions

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker (for running Qdrant locally)
- OpenAI API key

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/rag-chatbot.git
   cd rag-chatbot
   ```

2. Set up a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Create your environment file
   ```bash
   cp .env.example .env
   ```
   
5. Add your API keys to the `.env` file
   ```
   OPENAI_API_KEY=your_openai_api_key
   QDRANT_API_KEY=your_qdrant_api_key_if_using_cloud
   QDRANT_ENDPOINT_URL=your_qdrant_endpoint_if_using_cloud
   ```

### Setup Qdrant Vector Database

#### Option 1: Local Deployment (Docker)
```bash
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

#### Option 2: Cloud Service
Sign up at [Qdrant Cloud](https://cloud.qdrant.io/) and update your `.env` file with the credentials.

## 🔧 Usage

1. Start the backend API server
   ```bash
   cd api
   python main.py
   ```
   The API server will be available at http://localhost:8080

2. Launch the Streamlit application
   ```bash
   cd app
   streamlit run streamlit_app.py
   ```
   The UI will be available at http://localhost:8501

3. Upload documents, ask questions, and receive enhanced responses!

## 🏗️ Architecture

### Project Structure
```
.
├── .env                   # Environment variables
├── .gitignore             # Git ignore file
├── README.md              # This documentation
├── requirements.txt       # Python dependencies
├── api/                   # Backend API
│   ├── app.py             # FastAPI application
│   ├── main.py            # Entry point
│   ├── services/          # Service layer
│   │   ├── logger.py      # Logging configuration
│   │   └── pydantic_models.py # Data models
│   └── utils/             # Utility functions
│       ├── db_utils.py    # Database operations
│       ├── langchain_utils.py # Langchain configurations
│       ├── prompts.py     # LLM prompts
│       ├── qdrant_utils.py # Vector database operations
│       └── utils.py       # General utilities
└── app/                   # Frontend application
    ├── app_utils.py       # API communication
    ├── chat_interface.py  # Chat UI component
    ├── sidebar.py         # Sidebar UI component
    └── streamlit_app.py   # Main Streamlit application
```

### Data Flow
1. **Document Upload:** Documents are processed, chunked, and stored in Qdrant
2. **User Query:** User submits a question via the Streamlit UI
3. **Query Processing:** Backend refines the query using conversation context
4. **Retrieval:** Relevant document chunks are retrieved from Qdrant
5. **Generation:** OpenAI model generates a response based on retrieved context
6. **Response:** Answer is displayed to the user with source attribution

## 📡 API Endpoints

The application exposes the following RESTful API endpoints:

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|-------------|----------|
| `/upload_doc` | POST | Upload a document | `multipart/form-data` with file | Document ID and metadata |
| `/list_docs` | GET | List all documents | None | Array of document metadata |
| `/delete_doc` | POST | Delete a document | `{"file_id": "id"}` | Success status |
| `/chat` | POST | Ask a question | `{"question": "text", "session_id": "id", "model": "name"}` | AI response with metadata |

## 🛠️ Development

### Setting Up the Development Environment

1. Install development dependencies
   ```bash
   pip install -e ".[dev]"
   ```

2. Install pre-commit hooks
   ```bash
   pre-commit install
   ```

### Customization

- **Vector Database:** Configure Qdrant parameters in `api/utils/qdrant_utils.py`
- **Document Processing:** Adjust chunking in `api/utils/langchain_utils.py`
- **LLM Prompts:** Modify system prompts in `api/utils/prompts.py`

## 📊 Performance Considerations

- **Memory Usage:** Monitor RAM when processing large documents
- **API Rate Limits:** Be aware of OpenAI's rate limiting
- **Vector Database Scaling:** Consider Qdrant Cloud for production workloads
- **Embedding Dimensions:** Using 3072-dimensional OpenAI embeddings

## 🔒 Security

- API keys are stored in environment variables, not in code
- User sessions are isolated
- Document access is session-scoped

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
