import time
import langsmith as ls
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
    
async def retrieve_similar_documents(refined_query: str, num_of_chunks: int,username: str) -> str:
    pass

async def invoke_chain(query, context, history, llm):
    pass

def initialize_llm(model="gpt-3.5-turbo", temperature=0.0, llm_provider="openai"):
    pass
    
async def refine_user_query(query, messages):
    pass

def create_history(messages):
    """
    Create an InMemoryChatMessageHistory object from the given messages.
    """
    history = InMemoryChatMessageHistory()
    for message in messages:
            if message["role"] == "user":
                history.add_user_message(message["content"])
            else:
                history.add_ai_message(message["content"])

    return history

@ls.traceable(run_type="chain", name="Chat Pipeline")
async def generate_chatbot_response(query, past_messages, no_of_chunks,username):
    pass