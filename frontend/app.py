import streamlit as st
import requests

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Chatbot 🤖")

# Create a container for messages
chat_container = st.container()

# Display chat messages
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

# Chat input at the bottom
if user_input := st.chat_input("Type your message here..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    try:
        # Send request to backend
        response = requests.post(
            "http://backend:5000/chat",
            json={"message": user_input}
        )
        bot_reply = response.json().get("reply", "Sorry, I couldn't process that.")
        
        # Add bot response to history
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except requests.exceptions.RequestException as e:
        st.error("Failed to connect to the chatbot backend.")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Sorry, I'm having trouble connecting right now. Please try again later."
        })
    
    # Rerun to update the chat display
    st.rerun()

# Optional: Add a clear chat button
if st.session_state.messages:
    if st.button("Clear Chat", type="secondary"):
        st.session_state.messages = []
        st.rerun()