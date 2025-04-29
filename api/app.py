from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from services.logger import logger
from utils.langchain_utils import generate_chatbot_response, index_documents
from utils.utils import extract_text_from_file

load_dotenv()

app = FastAPI()
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Document Indexing and Chatbot API!"}

@app.post("/upload_doc")
async def upload_doc(session_id: str, file: Optional[UploadFile] = File(None)):
    try:
        extracted_text = ""
        logger.info(f"Request received: session_id={session_id}")
        
        if file:
            logger.info(f"File uploaded: {file.filename}, Content-Type: {file.content_type}")
            file_content = await file.read()
            logger.info(f"File content size: {len(file_content)} bytes")
            
            file_extension = file.filename.split(".")[-1].lower()
            logger.info(f"File extension detected: {file_extension}")
            
            extracted_text = await extract_text_from_file(file_content, file_extension)
            logger.info(f"Extracted text length: {len(extracted_text)} characters")

            logger.info(f"Indexing documents in QdrantDB")
            await index_documents(session_id, extracted_text, file.filename, file_extension)
        else:
            logger.warning("No file was uploaded in the request")
            
        return {
            "response": "Indexed Documents Successfully",
            "extracted_text": extracted_text[:100] + "..." if len(extracted_text) > 100 else extracted_text,
        }
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while indexing documents {e}",
        )


@app.post("/chat")
async def chat(question: str, session_id: str, model: str):
    return {"question": question, "session_id": session_id, "model": model}
