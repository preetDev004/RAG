# RAG - Bot

A Retrieval-Augmented Generation (RAG) chatbot application that allows users to upload documents, ask questions, and receive responses enhanced by the knowledge contained in those documents.

## Overview

This project implements a RAG system with a Streamlit frontend and API backend. It enables users to upload various document types, maintain a document library, and interact with powerful language models that utilize the information from these documents to provide more relevant and accurate responses.

## Features

- **Document Management**
  - Upload PDF, DOCX, and HTML documents
  - List all uploaded documents
  - Delete documents when no longer needed
  
- **AI Chat Interface**
  - Interactive chat with AI models
  - Choose between different OpenAI models (gpt-4o, gpt-4o-mini)
  - Session persistence for continuous conversations

- **Response Details**
  - View detailed information about generated responses
  - See which model was used
  - Track session IDs

## Installation

1. Clone the repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

1. Start the backend API server (not included in this repository)
   ```
   # Run the API server
   # Command depends on API implementation
   ```

2. Launch the Streamlit application:
   ```
   cd app
   streamlit run streamlit_app.py
   ```

3. Open your browser and navigate to the provided local URL (typically http://localhost:8501)

## Project Structure

```
.
├── .env                # Environment variables (API keys)
├── .gitignore          # Git ignore file
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
├── api/                # API backend (not fully visible in current workspace)
└── app/
    ├── app_utils.py    # Utility functions for API communication
    ├── chat_interface.py # Chat UI component
    ├── sidebar.py      # Sidebar UI component
    └── streamlit_app.py # Main Streamlit application
```

## API Endpoints

The application interacts with the following API endpoints:

- `POST /upload_doc` - Upload a document
- `GET /list_docs` - List all documents
- `POST /delete_doc` - Delete a document
- `POST /chat` - Send a query and get a response

## Current Development Stage

This project is currently in initial development. The frontend components and API integration are implemented, but the backend implementation may require additional work.

