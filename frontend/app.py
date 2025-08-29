import streamlit as st
import requests
import base64
from typing import List, Dict

# Configure page
st.set_page_config(
    page_title="Simple Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []



def send_message_to_backend(message: str) -> str:
    """Send message and files to backend, return response"""
    try:
        payload = {
            "message": message
        }
        
        response = requests.post(
            "http://chatbot_backend:5000/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("reply", "Sorry, I couldn't process that.")
        else:
            return f"❌ Server error: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to backend. Please check if the server is running."
    except requests.exceptions.Timeout:
        return "⏰ Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"❌ Connection error: {str(e)}"

# App header
st.title("🤖 Simple Chatbot")
st.write("Ask me anything!")


# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Prepare files for this message
    current_files = st.session_state.uploaded_files.copy() if st.session_state.uploaded_files else []
    
    # Add user message to chat history
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt
    })
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = send_message_to_backend(prompt)
        st.write(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response
    })

# Sidebar with chat controls
with st.sidebar:
    st.header("Chat Controls")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.uploaded_files = []
        st.rerun()
    
    st.write(f"💬 Messages: {len(st.session_state.messages)}")
    
    # Show connection status
    st.subheader("Connection Status")
    try:
        test_response = requests.get("http://chatbot_backend:5000/", timeout=2)
        if test_response.status_code == 404:  # Flask returns 404 for undefined routes
            st.success("✅ Backend Connected")
        else:
            st.success("✅ Backend Connected")
    except:
        st.error("❌ Backend Disconnected")