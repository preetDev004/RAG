import os
import aiosqlite
import uuid
from typing import List, Dict, Any
from services.logger import logger

# production (Huggingface Spaces)
# DB_DIR = "/home/user/db"

# local
DB_DIR = "./"
os.makedirs(DB_DIR, exist_ok=True)

DB_NAME = os.path.join(DB_DIR, "rag_app.db")

async def get_async_db_connection():
    """
    Get an async SQLite connection.
    """
    conn = await aiosqlite.connect(DB_NAME)
    conn.row_factory = aiosqlite.Row
    return conn

async def create_application_logs():
    """
    Create the application_logs table if it doesn't exist.
    """
    try:
        conn = await get_async_db_connection()
        try:
            await conn.execute(
                """CREATE TABLE IF NOT EXISTS application_logs
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            session_id TEXT,
                            user_query TEXT,
                            gpt_response TEXT,
                            model TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
            )
            await conn.commit()
            logger.info("Created application logs table if not exists")
        finally:
            await conn.close()

    except Exception as e:
        logger.error(
            f"An error occurred while creating the application logs table: {str(e)}"
        )
        raise e

async def insert_application_logs(session_id: str, user_query: str, gpt_response: str, model: str):
    """
    Insert a new log entry into the application_logs table.
    """
    try:
        conn = await get_async_db_connection()
        try:
            await conn.execute(
                "INSERT INTO application_logs (session_id, user_query, gpt_response, model) VALUES (?, ?, ?, ?)",
                (session_id, user_query, gpt_response, model),
            )
            await conn.commit()
            logger.info("Inserted into application logs table")
        finally:
            await conn.close()

    except Exception as e:
        logger.error(
            f"An error occurred while inserting into the application logs table: {str(e)}"
        )
        raise e


async def get_chat_history(session_id: str) -> List[Dict[str, str]]:
    """
    Get chat history for a specific session.
    """
    messages = []
    try:
        conn = await get_async_db_connection()
        try:
            async with conn.execute(
                'SELECT user_query, gpt_response FROM application_logs WHERE session_id = ? ORDER BY created_at', 
                (session_id,)
            ) as cursor:
                async for row in cursor:
                    messages.extend([
                        {"role": "human", "content": row['user_query']},
                        {"role": "ai", "content": row['gpt_response']}
                    ])
        finally:
            await conn.close()
        return messages
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        return messages


async def create_document_store():
    """
    Create the document_store table if it doesn't exist.
    """
    try:
        conn = await get_async_db_connection()
        try:
            await conn.execute('''CREATE TABLE IF NOT EXISTS document_store
                        (id TEXT PRIMARY KEY,
                         filename TEXT,
                         session_id TEXT NOT NULL,
                         upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            await conn.commit()
            logger.info("Created document store table if not exists")
        finally:
            await conn.close()
    except Exception as e:
        logger.error(f"Error creating document store: {str(e)}")
        raise e

async def insert_document_record(filename: str, session_id: str) -> str:
    """
    Insert a new document record and return its ID.
    
    Args:
        filename: The name of the file being stored
        session_id: The session ID that owns this document
        
    Returns:
        str: The generated document ID
    """
    try:
        conn = await get_async_db_connection()
        file_id = str(uuid.uuid4())
        try:
            await conn.execute('INSERT INTO document_store (id, filename, session_id) VALUES (?, ?, ?)', 
                              (file_id, filename, session_id))
            await conn.commit()
            logger.info(f"Inserted document with ID {file_id} for session {session_id}")
        finally:
            await conn.close()
        return file_id
    except Exception as e:
        logger.error(f"Error inserting document record: {str(e)}")
        raise e


async def delete_document_record(file_id: str, session_id: str) -> bool:
    """
    Delete a document record by ID but only if it belongs to the given session.
    
    Args:
        file_id: The document ID to delete
        session_id: The session ID that owns the document
        
    Returns:
        bool: True if document was successfully deleted, False otherwise
    """
    try:
        conn = await get_async_db_connection()
        try:
            # First verify the document belongs to this session
            async with conn.execute('SELECT id FROM document_store WHERE id = ? AND session_id = ?', 
                                  (file_id, session_id)) as cursor:
                if not await cursor.fetchone():
                    logger.warning(f"Attempted unauthorized deletion of document {file_id} by session {session_id}")
                    return False
                
            # If verification passes, delete the document
            await conn.execute('DELETE FROM document_store WHERE id = ? AND session_id = ?', 
                              (file_id, session_id))
            await conn.commit()
            logger.info(f"Document {file_id} deleted by its owner session {session_id}")
        finally:
            await conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting document record: {str(e)}")
        return False


async def get_all_documents(session_id: str) -> List[Dict[str, Any]]:
    """
    Get all documents for a specific session ordered by upload timestamp.
    
    Args:
        session_id: The session ID to filter documents by
        
    Returns:
        List[Dict[str, Any]]: List of document information
    """
    documents = []
    try:
        conn = await get_async_db_connection()
        try:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                'SELECT id, filename, upload_timestamp FROM document_store WHERE session_id = ? ORDER BY upload_timestamp DESC',
                (session_id,)
            ) as cursor:
                async for row in cursor:
                    documents.append(dict(row))
        finally:
            await conn.close()
        return documents
    except Exception as e:
        logger.error(f"Error retrieving documents for session {session_id}: {str(e)}")
        return documents


# Initialize the database tables
async def initialize_db():
    """Initialize all database tables"""
    await create_application_logs()
    await create_document_store()
    logger.info("Database initialized successfully")
