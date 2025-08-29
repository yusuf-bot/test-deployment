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
        # Send request to backend - Use correct container name
        response = requests.post(
            "http://chatbot_backend:5000/chat",  # Use actual container name
            json={"message": user_input},
            timeout=30  # Added timeout
        )
        
        if response.status_code == 200:
            bot_reply = response.json().get("reply", "Sorry, I couldn't process that.")
            # Add bot response to history
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        else:
            st.error(f"Backend returned status code: {response.status_code}")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"Server error: {response.status_code}"
            })
        
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure Flask server is running on port 5000.")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "❌ Backend server not running. Please start the Flask server first."
        })
    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. Please try again.")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "⏰ Request timed out. Please try again."
        })
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Request failed: {str(e)}")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"❌ Connection error: {str(e)}"
        })

# Add status indicator
if st.session_state.messages:
    with st.sidebar:
        st.subheader("Connection Status")
        try:
            test_response = requests.get("http://chatbot_backend:5000/", timeout=2)
            st.success("✅ Backend Connected")
        except:
            st.error("❌ Backend Disconnected")
            st.write("Make sure your Flask server is running:")
            st.code("python your_flask_file.py")