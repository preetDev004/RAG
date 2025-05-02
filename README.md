# Langchain RAG Chatbot

A production-ready Retrieval-Augmented Generation (RAG) system built with FastAPI, Langchain, and Qdrant vector database. This system lets you chat with your documents using OpenAI's large language models.

## Features

- 📄 Multi-document support (PDF, DOCX, TXT)
- 🔍 Semantic search with Qdrant vector database
- 💬 Conversational memory with session tracking
- 📊 Streamlit-based user interface
- 🚀 FastAPI backend for performance
- 📈 LangSmith integration for tracing and monitoring
- 📝 Document management (upload, list, delete)
- 🔄 Query refinement for better responses

## Architecture

The application consists of two main components:

1. **FastAPI Backend** (`/api`): Handles document processing, vector storage, and chat generation
2. **Streamlit Frontend** (`/app`): Provides a user-friendly interface for chatting and document management

### Backend Components

- **Document Processing**: Extract text from PDFs, DOCX, and TXT files
- **Vector Database**: Qdrant for semantic document storage
- **RAG Pipeline**: Query refinement, document retrieval, and response generation
- **Session Management**: Track conversations with persistent storage

### Frontend Components

- **Chat Interface**: Interactive chat UI with response streaming
- **Document Manager**: Upload, list, and delete documents
- **Model Selection**: Choose different OpenAI models for responses

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (for running Qdrant locally)
- OpenAI API key
- Qdrant Cloud account (or local Qdrant instance)
- LangSmith account (optional, for tracing)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/rag-chatbot.git
cd rag-chatbot
```

2. Set up environment variables
```bash
cp .env.example .env
# Edit the .env file with your API keys
```

3. Install backend dependencies
```bash
cd api
pip install -r requirements.txt
```

4. Install frontend dependencies
```bash
cd ../app
pip install streamlit requests
```

### Running the Application

1. Start the backend server
```bash
cd api
python main.py
```

2. Start the frontend application
```bash
cd app
streamlit run streamlit_app.py
```

## Usage

1. Open the Streamlit UI in your browser (typically at http://localhost:8501)
2. Upload documents using the sidebar
3. Ask questions about your documents in the chat interface
4. Switch between models using the sidebar dropdown

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Process a chat query and return AI response |
| `/upload-doc` | POST | Upload and index a document |
| `/list-docs` | GET | List all uploaded documents |
| `/delete-doc` | POST | Delete a document by ID |

## Project Structure

```
rag/
├── .env                    # Environment variables
├── README.md               # This file
├── rag_app.db              # SQLite database for storage
├── api/                    # Backend API
│   ├── app.py              # FastAPI application
│   ├── main.py             # Entry point
│   ├── requirements.txt    # Dependencies
│   ├── services/           # Service modules
│   └── utils/              # Utility functions
└── app/                    # Frontend Streamlit app
    ├── api_utils.py        # API client functions
    ├── chat_interface.py   # Chat UI components
    ├── sidebar.py          # Sidebar UI components
    └── streamlit_app.py    # Main Streamlit application
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `QDRANT_API_KEY` | Your Qdrant API key |
| `QDRANT_ENDPOINT_URL` | Qdrant Cloud endpoint or local URL |
| `LANGSMITH_TRACING` | Enable/disable LangSmith tracing |
| `LANGSMITH_API_KEY` | Your LangSmith API key |
| `LANGSMITH_PROJECT` | LangSmith project name |

## Advanced Features

### Query Refinement

The system uses LLMs to refine user queries before searching for documents, improving search relevance.

### Dynamic Chunk Sizing

Document chunks are dynamically sized based on content length for optimal retrieval.

### Session Management

Conversations are stored and retrieved by session ID, allowing for persistent chats.

## Performance Optimization

- Asynchronous processing with FastAPI and asyncio
- Efficient document chunking for better retrieval
- Caching of vector embeddings to reduce API calls
- Streaming responses for better user experience

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [Langchain](https://github.com/langchain-ai/langchain) for the RAG pipeline
- [Qdrant](https://github.com/qdrant/qdrant) for vector storage
- [FastAPI](https://github.com/tiangolo/fastapi) for the API framework
- [Streamlit](https://github.com/streamlit/streamlit) for the user interface
- [OpenAI](https://github.com/openai/openai-python) for language models