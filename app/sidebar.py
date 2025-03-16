import streamlit as st
from app_utils import upload_document, list_documents, delete_document


def display_sidebar():
    # Sidebar Model Selection
    model_options = ["gpt-4o", "gpt-4o-mini"]
    st.sidebar.selectbox("Select model", options=model_options, key="model")

    # Sidebar Upload Document
    st.sidebar.header("Upload Documents")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a File", type=["pdf", "docx", "html"]
    )
    if uploaded_file is not None:
        if st.sidebar.button("Upload"):
            with st.spinner("Uploading..."):
                upload_response = upload_document(uploaded_file)
                if upload_response:
                    st.sidebar.success(
                        f"File {uploaded_file.name} uploaded successfuly with id {uploaded_file['file_id']}."
                    )
                    st.session_state.documents = (
                        list_documents()
                    )  # refresh the docs after upload

    # Sidebar List Document
    st.sidebar.header("Current Documents")
    if st.sidebar.button("Refresh Doc List"):
        with st.spinner("Refreshing..."):
            st.session_state.documents = list_documents()

    # Initialize the document list if not present
    if "documents" not in st.session_state:
        st.session_state.documents = list_documents()

    documents = st.session_state.documents
    if documents:
        for doc in documents:
            st.sidebar.text(
                f"{doc['filename']} (ID: {doc['id']}, Uploaded: {doc['uploaded_timestamp']})"
            )

        # Delete Docs
        selected_file_id = st.sidebar.selectbox(
            "Select a Doc to delete",
            options=[doc["id"] for doc in documents],
            format_func=lambda x: next(
                doc["filename"] for doc in documents if doc["id"] == x
            ),
        )
        if st.sidebar.button("Deleting Selected Document"):
            delete_response = delete_document(selected_file_id)
            if delete_response:
                st.sidebar.success(f"Document with ID {selected_file_id} deleted successfully.")
                st.session_state.documents = list_documents()
            else:
                st.error(f"Failed to delete the document with ID {selected_file_id}.")
            