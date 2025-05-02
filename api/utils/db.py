import aiosqlite
import uuid
from typing import List, Dict, Any
from services.logger import logger

DB_NAME = "rag_app.db"


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
                         upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            await conn.commit()
            logger.info("Created document store table if not exists")
        finally:
            await conn.close()
    except Exception as e:
        logger.error(f"Error creating document store: {str(e)}")
        raise e


async def insert_document_record(filename: str) -> str:
    """
    Insert a new document record and return its ID.
    """
    try:
        conn = await get_async_db_connection()
        file_id = str(uuid.uuid4())
        try:
            await conn.execute('INSERT INTO document_store (id, filename) VALUES (?, ?)', (file_id, filename))
            await conn.commit()
            logger.info(f"Inserted document with ID {file_id}")
        finally:
            await conn.close()
        return file_id
    except Exception as e:
        logger.error(f"Error inserting document record: {str(e)}")
        raise e


async def delete_document_record(file_id: str) -> bool:
    """
    Delete a document record by ID.
    """
    try:
        conn = await get_async_db_connection()
        try:
            await conn.execute('DELETE FROM document_store WHERE id = ?', (file_id,))
            await conn.commit()
        finally:
            await conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting document record: {str(e)}")
        return False


async def get_all_documents() -> List[Dict[str, Any]]:
    """
    Get all documents ordered by upload timestamp.
    """
    documents = []
    try:
        conn = await get_async_db_connection()
        try:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                'SELECT id, filename, upload_timestamp FROM document_store ORDER BY upload_timestamp DESC'
            ) as cursor:
                async for row in cursor:
                    documents.append(dict(row))
        finally:
            await conn.close()
        return documents
    except Exception as e:
        logger.error(f"Error retrieving all documents: {str(e)}")
        return documents


# Initialize the database tables
async def initialize_db():
    """Initialize all database tables"""
    await create_application_logs()
    await create_document_store()
    logger.info("Database initialized successfully")

