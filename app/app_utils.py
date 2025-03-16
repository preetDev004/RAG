import streamlit as st
import requests


def upload_document(file):
    print("Uploading File...")
    try:
        files = {"file": (file.name, file, file.type)}
        response = requests.post("http://localhost:8080/upload_doc", files={files})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(
                f"Failed to upload the file: {response.status_code} - {response.text}"
            )
            return None
    except Exception as e:
        st.error(f"An Error occured while uploading the file: {str(e)}")
        return None


def get_api_response(question, session_id, model):
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {question: question, session_id: session_id, model: model}
    try:
        response = requests.post(
            "http://localhost:8080/chat", headers=headers, json=data
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API request Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An Error occured: {str(e)}")
        return None


def list_documents():
    try:
        response = requests.get("http://localhost:8080/list_docs")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(
                f"Failed to fetch the documents: {response.status_code} - {response.text}"
            )
            return []
    except Exception as e:
        st.error(f"An Error occured: {str(e)}")
        return []


def delete_document(file_id):
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {"file_id": file_id}
    try:
        response = requests.post(
            "http://localhost:8080/delete_doc", headers=headers, json=data
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(
                f"Failed to delere the document: {response.status_code} - {response.text}"
            )
            return None
    except Exception as e:
        st.error(f"An error occured while deleting the file: {file_id}")
        return None
