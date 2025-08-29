import streamlit as st
import requests
import base64
from typing import List, Dict, Any
import os

# Configure page
st.set_page_config(
    page_title="Claude-like Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Claude-like UI
st.markdown("""
<style>
    /* Hide default streamlit elements */
    .stDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    header[data-testid="stHeader"] {display: none;}
    
    /* Main container styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 800px;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        line-height: 1.6;
    }
    
    .user-message {
        background-color: #f8f9fa;
        border-left: 3px solid #007acc;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background-color: #ffffff;
        border-left: 3px solid #00d4aa;
        margin-right: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* File upload styling */
    .uploaded-file {
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
        border-radius: 4px;
        padding: 0.5rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    /* Input area styling */
    .stChatInput > div > div > textarea {
        border-radius: 12px;
        border: 1px solid #d1d5db;
        padding: 12px 16px;
    }
    
    /* Header styling */
    .chat-header {
        text-align: center;
        padding: 1rem 0 2rem 0;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    
    /* File attachment button */
    .file-upload-section {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px dashed #d1d5db;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

def encode_file_to_base64(uploaded_file) -> str:
    """Convert uploaded file to base64 string"""
    try:
        file_content = uploaded_file.getvalue()
        encoded = base64.b64encode(file_content).decode('utf-8')
        return encoded
    except Exception as e:
        st.error(f"Error encoding file: {str(e)}")
        return ""

def display_message(role: str, content: str, files: List[Dict] = None):
    """Display a chat message with proper styling"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
        
        # Display attached files for user messages
        if files:
            for file_info in files:
                st.markdown(f"""
                <div class="uploaded-file">
                    📎 {file_info['name']} ({file_info['type']}, {file_info['size']} bytes)
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>Assistant</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)

def send_message_to_backend(message: str, files: List[Dict] = None) -> str:
    """Send message and files to backend"""
    try:
        payload = {
            "message": message,
            "files": files or []
        }
        
        response = requests.post(
            "http://chatbot_backend:5000/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get("reply", "Sorry, I couldn't process that.")
        else:
            return f"❌ Server error: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to backend. Please check if the server is running."
    except requests.exceptions.Timeout:
        return "⏰ Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"❌ Connection error: {str(e)}"

# Header
st.markdown("""
<div class="chat-header">
    <h1>🤖 Claude-like Chatbot</h1>
    <p style="color: #666; margin: 0;">Ask me anything or upload files for analysis</p>
</div>
""", unsafe_allow_html=True)

# File upload section
with st.expander("📎 Attach Files", expanded=False):
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        accept_multiple_files=True,
        type=['txt', 'pdf', 'docx', 'csv', 'json', 'py', 'js', 'html', 'css', 'md'],
        key="file_uploader"
    )
    
    if uploaded_files:
        st.session_state.uploaded_files = []
        for uploaded_file in uploaded_files:
            file_info = {
                "name": uploaded_file.name,
                "type": uploaded_file.type,
                "size": uploaded_file.size,
                "content": encode_file_to_base64(uploaded_file)
            }
            st.session_state.uploaded_files.append(file_info)
        
        st.success(f"✅ {len(uploaded_files)} file(s) ready to send")
        for file in uploaded_files:
            st.write(f"📄 {file.name} ({file.type})")

# Chat messages container
chat_container = st.container()

with chat_container:
    # Display all messages
    for message in st.session_state.messages:
        display_message(
            message["role"], 
            message["content"], 
            message.get("files", [])
        )

# Chat input
if user_input := st.chat_input("Type your message here..."):
    # Prepare files for this message
    current_files = st.session_state.uploaded_files.copy() if st.session_state.uploaded_files else []
    
    # Add user message immediately to show it
    user_message = {
        "role": "user", 
        "content": user_input,
        "files": current_files
    }
    st.session_state.messages.append(user_message)
    
    # Display the user message immediately
    with chat_container:
        display_message(user_message["role"], user_message["content"], user_message.get("files", []))
    
    # Send to backend and get response
    with st.spinner("🤔 Thinking..."):
        bot_reply = send_message_to_backend(user_input, current_files)
    
    # Add bot response
    assistant_message = {
        "role": "assistant", 
        "content": bot_reply
    }
    st.session_state.messages.append(assistant_message)
    
    # Clear uploaded files after sending
    st.session_state.uploaded_files = []
    
    # Rerun to show the new messages
    st.rerun()

# Sidebar with connection status and controls
with st.sidebar:
    st.subheader("🔗 Connection Status")
    try:
        test_response = requests.get("http://chatbot_backend:5000/", timeout=2)
        st.success("✅ Backend Connected")
    except:
        st.error("❌ Backend Disconnected")
    
    st.divider()
    
    st.subheader("💬 Chat Controls")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.uploaded_files = []
        st.rerun()
    
    st.subheader("📊 Chat Stats")
    st.metric("Messages", len(st.session_state.messages))
    
    if st.session_state.messages:
        user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
        assistant_msgs = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        st.metric("Your Messages", user_msgs)
        st.metric("Assistant Replies", assistant_msgs)

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666; font-size: 0.9rem; border-top: 1px solid #e5e7eb; margin-top: 2rem;">
    💡 Tip: You can upload multiple files and ask questions about them!
</div>
""", unsafe_allow_html=True)