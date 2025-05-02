import time
import os
import langsmith as ls
from services.logger import logger
from utils.qdrant import DocumentIndexer
from utils.prompts import get_query_refiner_prompt, get_main_prompt
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback


async def format_doc(docs):
    """
    Format the documents for display.
    """
    return "\n\n".join(doc.page_content for doc in docs)


async def index_documents(
    session_id: str, extracted_text: str, filename: str, file_extension: str
):
    """
    Index the document into Qdrant.
    """
    indexer = DocumentIndexer()
    start_time = time.time()
    logger.info("Searching for similar documents...")

    try:
        await indexer.index_into_qdrant(
            extracted_text=extracted_text,
            file_id=filename,  # Changed from file_name to file_id to match parameter name
            doc_type=file_extension,
            chunk_size=1500,
        )
        logger.info(
            f"Document indexing completed in {time.time() - start_time:.2f} seconds"
        )

    except Exception as e:
        logger.error(f"Error during document indexing: {e}")
        raise e


async def retrieve_similar_documents(
    refined_query: str, num_of_chunks: str, session_id: str
):
    """
    Retrieve similar documents from Qdrant based on the refined query.
    """
    try:
        indexer = DocumentIndexer()
        start_time = time.time()
        logger.info("Searching for similar documents in Qdrant...")

        if num_of_chunks == None:
            num_of_chunks = 3
        if not isinstance(num_of_chunks, int) or num_of_chunks <= 0:
            raise ValueError("num_of_chunks must be a positive integer")

        retriever = await indexer.get_retriever(top_k=num_of_chunks)
        if not retriever:
            raise ValueError("Retriever is not initialized")

        retrieved_docs = await retriever.ainvoke(refined_query)
        if not retrieved_docs:
            extracted_text = ""
        else:
            extracted_text = await format_doc(retrieved_docs)

        logger.info(
            f"Document retrieval and formatting completed in {time.time() - start_time:.2f} seconds"
        )
        return extracted_text, retrieved_docs

    except Exception as e:
        logger.error(f"Error during similar document retrieval: {e}")
        raise RuntimeError(f"Failed to process documents: {str(e)}")


async def invoke_chain(query, context, history, llm):
    """
    Invoke the main chain with the provided query, context, and history.
    """
    logger.info("Initializing chain...")
    final_chain = get_main_prompt() | llm | StrOutputParser()
    logger.info("Chain is Initialized!")

    input_data = {
        "user_query": query,
        "context": context,
        "messages": history.messages,  # Pass the messages list, not the history object itself
    }
    logger.info(f"Input data: {input_data}")

    with get_openai_callback() as cb:
        final_response = await final_chain.ainvoke(input_data)  # Asynchronous method
        return final_response, cb


def initialize_llm(model="gpt-4o-mini", temperature=0.0, llm_provider="openai"):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    logger.info(f"Using OpenAI API key: {openai_api_key[:5]}...{openai_api_key[-5:]}")

    if llm_provider == "openai":
        logger.info(f"Initializing OpenAI model with values {model} and {temperature}")
        llm = ChatOpenAI(
            temperature=temperature, model_name=model, streaming=True, stream_usage=True,
            api_key=openai_api_key  # Explicitly pass API key here
        )
        return llm
    return None


async def refine_user_query(query, messages):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(temperature=0.0, model_name="gpt-4o-mini", api_key=openai_api_key)
    history = create_history(messages)
    prompt = get_query_refiner_prompt()
    refined_query_chain = prompt | llm | StrOutputParser()

    refined_query = await refined_query_chain.ainvoke(
        {"query": query, "messages": history.messages}
    )
    return refined_query


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
async def generate_chatbot_response(
    query, past_messages, session_id, no_of_chunks: int = 3
):
    """
    Generate a chatbot response based on the user query and past messages.
    """
    logger.info("Refining user query...")
    refined_query = await refine_user_query(query, past_messages)
    logger.info("Refined user query: " + refined_query)

    extracted_text, retrieved_docs = await retrieve_similar_documents(
        refined_query, no_of_chunks, session_id
    )
    logger.info("Extracted text: " + extracted_text)
    logger.info("Retrieved documents: " + str(retrieved_docs))

    llm = initialize_llm()
    history = create_history(past_messages)
    logger.info(f"Created history for session: {history}")

    logger.info("Fetching response")
    start_time = time.time()
    final_response, cb = await invoke_chain(
        query, extracted_text, history, llm
    )  # Async call
    response_time = time.time() - start_time

    logger.info(f"Got response from chain:")
    return (
        final_response,
        response_time,
        cb.prompt_tokens,
        cb.completion_tokens,
        cb.total_tokens,
        extracted_text,
        refined_query,
        retrieved_docs,
    )