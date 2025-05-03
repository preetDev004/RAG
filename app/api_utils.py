import os
import requests
import streamlit as st

api_url = os.getenv("API_URL")

def get_api_response(question, session_id, model):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        "question": question,
        "model": model
    }
    if session_id:
        data["session_id"] = session_id

    try:
        response = requests.post(f"{api_url}/chat", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API request failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def upload_document(file):
    print("Uploading file...")
    try:
        files = {"file": (file.name, file, file.type)}
        response = requests.post(f"{api_url}/upload-doc", files=files)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to upload file. Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while uploading the file: {str(e)}")
        return None

def list_documents():
    try:
        # Get session_id from session state, or use None if not found
        session_id = st.session_state.get('session_id')
        
        if not session_id:
            st.warning("No session ID found. Please upload a document first to create a session.")
            return []
            
        # Include the session_id as a query parameter
        response = requests.get(f"{api_url}/list-docs", params={"session_id": session_id})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch document list. Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"An error occurred while fetching the document list: {str(e)}")
        return []

def delete_document(file_id):
    try:
        # Get session_id from session state
        session_id = st.session_state.get('session_id')
        
        if not session_id:
            st.error("No session ID found. Unable to delete document.")
            return False
            
        # Create delete request payload with file_id and session_id
        payload = {"file_id": file_id, "session_id": session_id}
        
        response = requests.post(f"{api_url}/delete-doc", json=payload)
        if response.status_code == 200:
            st.success("Document deleted successfully.")
            return True
        else:
            st.error(f"Failed to delete document. Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"An error occurred while deleting the document: {str(e)}")
        return False