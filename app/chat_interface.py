import streamlit as st
from app_utils import get_api_response

def display_chat_interface():
    # Chat Interface
    # Display past messages from the session state
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # Handle new user input
    if prompt := st.chat_input('Ask a question about your documents...'):
        # Make sure we have a session ID
        if not st.session_state.session_id:
            st.error("No active session. Please refresh the page.")
            return
        
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message('user'):
            st.markdown(prompt)
        
        # Generate and display response
        with st.status("Generating response..."):
            response = get_api_response(prompt, st.session_state.session_id, st.session_state.model)
            
            if response:
                # Update session ID if it changed
                if response.get('session_id') != st.session_state.session_id:
                    st.session_state.session_id = response.get('session_id')
                
                # Add assistant message to session state
                st.session_state.messages.append({"role": "assistant", "content": response['response']})
            
                # Display assistant message
                with st.chat_message('assistant'):
                    st.markdown(response['response'])

                    # Show details in an expander
                    with st.expander('Response Details'):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader('Generated Answer')
                            st.write(response['response'])
                            
                            st.subheader('Original Question')
                            st.write(response['question'])
                            
                            st.subheader('Refined Question')
                            st.write(response['refine_question'])
                        
                        with col2:
                            st.subheader('Model Used')
                            st.write(response.get('debug_info', {}).get('model', 'unknown'))
                            
                            st.subheader("Session ID")
                            st.code(response['session_id'])
                            
                            if 'debug_info' in response:
                                debug = response['debug_info']
                                st.subheader("Response Stats")
                                st.write(f"⏱️ Response time: {debug.get('response_time', 0):.2f}s")
                                st.write(f"🔤 Prompt tokens: {debug.get('prompt_tokens', 0)}")
                                st.write(f"🔤 Completion tokens: {debug.get('completion_tokens', 0)}")
                                st.write(f"🔤 Total tokens: {debug.get('total_tokens', 0)}")
            else:
                st.error("Failed to generate response. Please try again.")

