import time
from qdrant_utils import DocumentIndexer
from services.logger import logger
from langchain_core.chat_history import InMemoryChatMessageHistory

async def format_doc(docs):
    """
    Format the documents for display.
    """
    return "\n\n".join(doc.page_content for doc in docs)


async def index_document(extracted_text, filename, file_extension):
    indexer = DocumentIndexer()
    start_time = time.time()
    logger.info("Searching for similar documents...")

    try:
        await indexer.index_into_qdrant(
            extracted_text=extracted_text,
            file_name=filename,
            doc_type=file_extension,
            chunk_size=1500,
        )
        logger.info(f"Document indexing completed in {time.time() - start_time:.2f} seconds")

    except Exception as e:
        logger.error(f"Error during document indexing: {e}")
        raise e
    
def create_history(messages):
    history = InMemoryChatMessageHistory()
    for message in messages:
            if message["role"] == "user":
                history.add_user_message(message["content"])
            else:
                history.add_ai_message(message["content"])

    return history