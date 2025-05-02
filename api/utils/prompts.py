from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from services.logger import logger


def get_main_prompt():
    prompt = """
    "You are an assistant that helps users to find the best possible answer to their questions."
    "use the following pieces of retrieved context to answer the question at the end."
    "If you don't know the answer, just say that you don't know, don't try to make up an answer."
    """
    prompt = prompt + "\n\n" + "{context}"

    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("human", "{user_query}"),
        ]
    )
    logger.debug(f"Main Prompt: {final_prompt}")
    return final_prompt


def get_query_refiner_prompt():
    contextualize_q_system_prompt = """
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as it is."
    """
    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("human", "{query}"),
        ]
    )

    logger.debug(f"Query Refiner Prompt: {final_prompt}")
    return final_prompt
