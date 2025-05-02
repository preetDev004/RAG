from services.logger import logger
from fastapi import FastAPI, File, UploadFile, HTTPException
from services.pydantic_models import (
    QueryInput,
    QueryResponse,
    DocumentInfo,
    DeleteFileRequest,
)
from utils.langchain import generate_chatbot_response
from utils.db import (
    insert_application_logs,
    get_chat_history,
    get_all_documents,
    insert_document_record,
    delete_document_record,
    initialize_db,
)
from utils.qdrant import DocumentIndexer
from utils.utility import extract_text_from_file
import os
import uuid
import shutil
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code: initialize database
    await initialize_db()
    yield
    # Shutdown code (if any) would go here


app = FastAPI(lifespan=lifespan)


@app.post("/chat", response_model=QueryResponse)
async def chat(query_input: QueryInput):
    """
    Process a chat query and return AI response using RAG with Qdrant.

    Args:
        query_input: QueryInput containing question, session_id, and model

    Returns:
        QueryResponse: AI response with session ID and model information
    """
    try:
        session_id = query_input.session_id
        logger.info(
            f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}"
        )

        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session ID: {session_id}")

        # Get chat history asynchronously
        chat_history = await get_chat_history(session_id)

        # Use generate_chatbot_response instead of raw chain for better RAG integration
        (
            final_response,
            response_time,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            context_text,
            refined_query,
            retrieved_docs,
        ) = await generate_chatbot_response(
            query_input.question,
            chat_history,
            session_id,
            3,  # Number of chunks to retrieve
        )

        # Log response asynchronously
        await insert_application_logs(
            session_id, query_input.question, final_response, query_input.model.value
        )

        logger.info(
            f"Session ID: {session_id}, AI Response generated in {response_time:.2f}s, Tokens: {total_tokens}"
        )

        return QueryResponse(
            answer=final_response, session_id=session_id, model=query_input.model
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process chat request: {str(e)}"
        )


@app.post("/upload-doc")
async def upload_and_index_document(file: UploadFile = File(...)):
    """
    Upload and index a document in both the database and Qdrant vector store.

    Args:
        file: The file to upload

    Returns:
        dict: Result message and file ID

    Raises:
        HTTPException: If file type is unsupported or indexing fails
    """
    allowed_extensions = [".pdf", ".docx", ".txt"]
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}",
        )

    temp_file_path = f"temp_{file.filename}"

    try:
        # Save the uploaded file to a temporary file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Insert document record into database first
        file_id = await insert_document_record(file.filename)
        logger.info(f"Document record created with ID {file_id}")

        # Read file content
        with open(temp_file_path, "rb") as file_content:
            binary_content = file_content.read()

        # Extract text based on file type
        doc_type = file_extension.replace(".", "")
        extracted_text = await extract_text_from_file(binary_content, doc_type)

        if not extracted_text:
            logger.error(f"Failed to extract text from {file.filename}")
            await delete_document_record(file_id)
            raise HTTPException(
                status_code=500, detail=f"Failed to extract text from {file.filename}"
            )

        # Index document in Qdrant vector store
        try:
            # Initialize the DocumentIndexer
            indexer = DocumentIndexer()
            # Index the extracted text into Qdrant
            success = await indexer.index_into_qdrant(
                extracted_text=extracted_text,
                file_id=file_id, 
                doc_type=doc_type,
                chunk_size=None,  # Use dynamic chunk sizing
            )

            if not success:
                logger.error(f"Failed to index document {file.filename} into Qdrant")
                # Clean up the document record if indexing fails
                await delete_document_record(file_id)
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to index {file.filename} into vector database",
                )

            return {
                "message": f"File {file.filename} has been successfully uploaded and indexed in Qdrant.",
                "file_id": file_id,
            }

        except Exception as e:
            # Clean up the document record if indexing fails
            logger.error(f"Error during document indexing: {str(e)}")
            await delete_document_record(file_id)
            raise HTTPException(
                status_code=500, detail=f"Failed to index {file.filename}: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error uploading document: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.get("/list-docs", response_model=list[DocumentInfo])
async def list_documents():
    """
    Get a list of all documents in the document store.

    Returns:
        list[DocumentInfo]: List of document information objects
    """
    try:
        documents = await get_all_documents()
        return documents
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve documents: {str(e)}"
        )


@app.post("/delete-doc")
async def delete_document(request: DeleteFileRequest):
    """
    Delete a document from both the Qdrant vector store and database.

    Args:
        request: DeleteFileRequest containing the file_id to delete

    Returns:
        dict: Result message indicating success or failure
    """
    try:
        # Initialize the DocumentIndexer
        indexer = DocumentIndexer()

        # Delete from Qdrant vector store first
        try:
            # Use delete_chunks_by_file_id instead of delete_doc_from_chroma
            deleted_count = await indexer.delete_chunks_by_file_id(request.file_id)

            if deleted_count <= 0:
                logger.warning(
                    f"No chunks found to delete for file_id {request.file_id} in Qdrant"
                )
            else:
                logger.info(
                    f"Deleted {deleted_count} chunks for file_id {request.file_id} from Qdrant"
                )

        except Exception as e:
            logger.error(
                f"Failed to delete document with file_id {request.file_id} from Qdrant: {str(e)}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete document with file_id {request.file_id} from vector store: {str(e)}",
            )

        # If successfully deleted from vector store (or if no chunks were found),
        # proceed with deleting from database
        db_delete_success = await delete_document_record(request.file_id)

        if not db_delete_success:
            logger.error(
                f"Document deleted from Qdrant but failed to delete from database for file_id {request.file_id}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Document deleted from vector store but failed to delete from database",
            )

        return {
            "message": f"Successfully deleted document with file_id {request.file_id} from Qdrant and database"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete document: {str(e)}"
        )
