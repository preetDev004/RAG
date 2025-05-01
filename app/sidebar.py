import streamlit as st
from app_utils import upload_document, list_documents, delete_document, format_file_size


def display_sidebar():
    """Display the sidebar with document management functionality."""
    st.sidebar.title("Document Assistant")
    
    # Show current model info - simple caption
    st.sidebar.caption(f"Using model: gpt-4o-mini")
    
    # Document Upload Section - kept minimal
    st.sidebar.header("📄 Upload Document")
    
    # Use a key without using session_state directly
    uploaded_file = st.sidebar.file_uploader(
        "Upload PDF, Word, or text files",
        type=["pdf", "docx", "txt", "html"],
        help="Upload your documents to chat with them",
        key="file_uploader"  # Simple key that won't be modified directly
    )
    
    # Upload button appears only when file is selected
    if uploaded_file is not None:
        upload_button_pressed = st.sidebar.button(
            "Upload Document", 
            type="primary", 
            use_container_width=True,
            key="upload_btn"
        )
        
        # Handle upload after button press
        if upload_button_pressed:
            # Use status to show progress
            with st.sidebar.status("Uploading document..."):
                upload_response = upload_document(uploaded_file, st.session_state.session_id)
                
                if upload_response:
                    st.sidebar.success(f"✅ '{uploaded_file.name}' uploaded!")
                    
                    # Refresh documents list after successful upload
                    st.session_state.documents = list_documents(st.session_state.session_id)
                    
                    # Force a rerun to reset the UI state (this will clear the file uploader)
                    st.rerun()
                else:
                    st.sidebar.error("Upload failed!")

    # Documents Section - clean and minimal
    st.sidebar.markdown("---")
    st.sidebar.header("📚 Your Documents")
    
    # Simple refresh button
    if st.sidebar.button("🔄 Refresh", type="secondary", key="refresh_docs"):
        with st.sidebar.status("Refreshing documents..."):
            st.session_state.documents = list_documents(st.session_state.session_id)
            st.rerun()

    # Initialize document list if not present
    if "documents" not in st.session_state or not st.session_state.documents:
        with st.sidebar.status("Loading documents..."):
            st.session_state.documents = list_documents(st.session_state.session_id) or []
    
    # Display document list - clean and minimal
    documents = st.session_state.documents
    
    # Create deletion status key if not exists
    if "delete_status" not in st.session_state:
        st.session_state.delete_status = None
    
    # Show deletion status if any
    if st.session_state.delete_status:
        if st.session_state.delete_status["success"]:
            st.sidebar.success(st.session_state.delete_status["message"])
        else:
            st.sidebar.error(st.session_state.delete_status["message"])
        # Clear status after showing
        st.session_state.delete_status = None
    
    # Display documents
    if documents:
        for doc in documents:
            with st.sidebar.container():
                # Display document name with cleaner layout
                cols = st.sidebar.columns([4, 1])
                
                with cols[0]:
                    st.write(f"**{doc.get('filename', 'Unnamed')}**")
                
                with cols[1]:
                    # Create a unique delete button for each document
                    if st.button("🗑️", key=f"delete_{doc.get('id')}", help="Delete document"):
                        # Directly delete the document without confirmation
                        with st.spinner(f"Deleting {doc.get('filename')}..."):
                            delete_response = delete_document(doc.get('id'), st.session_state.session_id)
                            
                            if delete_response and delete_response.get("status") == "success":
                                st.session_state.delete_status = {
                                    "success": True,
                                    "message": f"Document deleted successfully"
                                }
                                # Refresh document list
                                st.session_state.documents = list_documents(st.session_state.session_id)
                            else:
                                st.session_state.delete_status = {
                                    "success": False,
                                    "message": "Failed to delete document"
                                }
                        st.rerun()
    else:
        st.sidebar.info("No documents available. Upload a document to get started.")
