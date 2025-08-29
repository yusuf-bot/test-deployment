import streamlit as st
import requests

st.title("Chatbot 🤖")

user_input = st.text_input("You:", "")

if st.button("Send"):
    response = requests.post(
        "http://backend:5000/chat",  # talks to Flask container
        json={"message": user_input}
    )
    bot_reply = response.json().get("reply", "")
    st.write(f"Bot: {bot_reply}")
