import streamlit as st
from app_utils import get_api_response

def display_chat_interface():
    # Chat Interface
    # Display past messages from the session state
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # Handle new user input
    if prompt := st.chat_input('Query:'):
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message('user'):
            st.markdown(prompt)
        
        # Generate and display response
        with st.spinner("Generating Response..."):
            response = get_api_response(prompt, st.session_state.session_id, st.session_state.model)
            
            if response:
                # Update session ID
                st.session_state.session_id = response.get('session_id')
                
                # Add assistant message to session state
                st.session_state.messages.append({"role":"assistant", "content": response['response']})
            
                # Display assistant message
                with st.chat_message('assistant'):
                    st.markdown(response['response'])

                    # Show details in an expander
                    with st.expander('Details'):
                        st.subheader('Generated Answer')
                        st.code(response['response'])
                        st.subheader('Model Used')
                        st.code(response.get('debug_info', {}).get('model', 'unknown'))
                        st.subheader("Session ID")
                        st.code(response['session_id'])
            else:
                st.error("Failed to generate response. Please try again.")

