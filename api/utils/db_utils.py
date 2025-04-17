import sqlite3
import aiosqlite
import asyncio
from typing import List
from services.logger import logger


def get_db_connection():
    """
    Simulate a database connection using in-memory SQLite DB.
    """
    connection = sqlite3.connect(":memory:")  # This will create an in-memory SQLite DB
    return connection, connection.cursor()


async def get_past_conversations(session_id: str) -> List[dict]:
    start_time = asyncio.get_event_loop().time()
    messages = []

    try:
        async with aiosqlite.connect("chat_log.db") as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    gpt_response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            logger.info("Created Db table if not exists")

            # Fetch Chat Logs for the given session_id
            async with connection.execute(
                """
                SELECT user_query, gpt_response, created_at
                FROM chat_logs
                WHERE session_id = ?
                ORDER BY created_at DESC
            """,
                (session_id,),
            ) as cursor:
                async for row in cursor:
                    message_user = {"role": "user", "content": row[0]}
                    message_gpt = {"role": "assistant", "content": row[1]}
                    messages.extend([message_user, message_gpt])

        elapsed_time = asyncio.get_event_loop().time() - start_time
        logger.info(
            f"Fetched past conversations - {messages} in {elapsed_time:.2f} seconds"
        )
        return messages

    except Exception as e:
        logger.error(f"An Error occured: {str(e)}")
        raise e


async def add_conversation_async(session_id: str, user_query: str, gpt_response: str):
    try:
        async with aiosqlite.connect("chat_log.db") as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    gpt_response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            logger.info("Created Db table if not exists")

            # Insert the conversation into the database
            await connection.execute(
                """
                INSERT INTO chat_logs (session_id, user_query, gpt_response)
                VALUES (?, ?, ?)
            """,
                (session_id, user_query, gpt_response),
            )

            await connection.commit()
            logger.info(f"Added conversation for session_id: {session_id}")
    except Exception as e:
        logger.error(f"An Error occured while adding the conversation: {str(e)}")
        raise e

async def get_documents(session_id: str) -> List[dict]:
    start_time = asyncio.get_event_loop().time()
    docs = []

    try:
        async with aiosqlite.connect("docs.db") as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS docs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        file_name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
            """
            )
            logger.info("Created Db table if not exists")

            # Fetch Chat Logs for the given session_id
            async with connection.execute(
                """
                SELECT id
                FROM docs
                WHERE session_id = ?
                ORDER BY created_at DESC
            """,
                (session_id,),
            ) as cursor:
                async for row in cursor:
                    docs.append({"id": row[0]})

    except Exception as e:
        logger.error(f"An Error occured: {str(e)}")
        raise e

    elapsed_time = asyncio.get_event_loop().time() - start_time
    logger.info(f"Fetched docs - {docs} in {elapsed_time:.2f} seconds")
    return docs

async def add_document_async(session_id: str, file_name: str):
    try:
        async with aiosqlite.connect("docs.db") as connection:
            await connection.execute(
                """
                INSERT INTO docs (session_id, file_name)
                VALUES (?, ?)
            """,
                (session_id, file_name),
            )

            await connection.commit()
            logger.info(f"Added document for session_id: {session_id}")
    except Exception as e:
        logger.error(f"An Error occured while adding the document: {str(e)}")
        raise e 

async def delete_document_async(session_id: str, file_name: str, id: int):
    try:
        async with aiosqlite.connect("docs.db") as connection:
            await connection.execute(
                """
                DELETE FROM docs
                WHERE session_id = ? AND file_name = ? AND id = ?
            """,
                (session_id, file_name, id),
            )

            await connection.commit()
            logger.info(f"Deleted document for session_id: {session_id}")
    except Exception as e:
        logger.error(f"An Error occured while deleting the document: {str(e)}")
        raise e