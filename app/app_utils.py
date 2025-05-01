import streamlit as st
import requests
import os
from typing import Dict, Any, Optional, List


API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def create_or_get_session(current_session_id=None):
    """
    Create a new session or extend the current one.
    """
    try:
        # Pass the existing session ID via cookies if available
        cookies = {}
        if current_session_id:
            cookies["session_id"] = current_session_id
            
        response = requests.post(f"{API_BASE_URL}/session", cookies=cookies)
        
        if response.status_code == 200:
            session_data = response.json()
            
            # Store the session ID from the response
            session_id = session_data.get("session_id")
            
            # Also store any cookies returned (the API sets the session as a cookie)
            if "session_id" in response.cookies:
                # Use the non-experimental cookie setter
                st.session_state.session_cookie = response.cookies.get("session_id")
                
            return session_data
        else:
            st.error(f"Failed to create session: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while creating session: {str(e)}")
        return None


def upload_document(file, session_id):
    """
    Upload a document to the API.
    """
    try:
        files = {"file": (file.name, file, file.type)}
        params = {"session_id": session_id} if session_id else {}
        
        response = requests.post(f"{API_BASE_URL}/upload_doc", params=params, files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to upload the file: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while uploading the file: {str(e)}")
        return None


def get_api_response(question, session_id, model):
    """
    Send a question to the API and get a response.
    """
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {"question": question, "session_id": session_id, "model": model}
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat", headers=headers, json=data
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None


def list_documents(session_id):
    """
    List all documents for the current session.
    """
    if not session_id:
        return []
        
    try:
        response = requests.get(f"{API_BASE_URL}/list_docs", params={"session_id": session_id})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch documents: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"An error occurred while fetching documents: {str(e)}")
        return []


def delete_document(doc_id, session_id):
    """
    Delete a document by its ID.
    """
    try:
        # Fixed - the API expects doc_id as a query parameter, not in JSON body
        response = requests.post(
            f"{API_BASE_URL}/delete_doc",
            params={
                "doc_id": doc_id,
                "session_id": session_id
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to delete document: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while deleting the document: {str(e)}")
        return None


def format_file_size(size_bytes):
    """
    Format file size in bytes to a human-readable format.
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
