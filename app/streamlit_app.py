import streamlit as st
from sidebar import display_sidebar
from chat_interface import display_chat_interface
from app_utils import create_or_get_session

# Set page configuration
st.set_page_config(
    page_title="Langchain RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("Langchain RAG Chatbot")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    # Try to get session from cookie or create a new one
    session_data = create_or_get_session()
    if session_data:
        st.session_state.session_id = session_data["session_id"]
        st.session_state.session_expiry = session_data["expiry"]
    else:
        st.session_state.session_id = None
        st.session_state.session_expiry = None

# Always use gpt-4o-mini by default
st.session_state.model = "gpt-4o-mini"

if "documents" not in st.session_state:
    st.session_state.documents = []

# Display session info in a small text at the top
if st.session_state.session_id:
    st.caption(f"Session ID: {st.session_state.session_id[:8]}... (expires: {st.session_state.session_expiry})")

# Display the sidebar and chat interface
display_sidebar()
display_chat_interface()