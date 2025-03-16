import streamlit as st
import requests
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI backend URL
BACKEND_URL = "http://localhost:8000"

# Streamlit app
st.title("Chat with your Document Engine")
st.write("Upload your document and interract with it !!")

# Initialize session state for user and chat management
if "userID" not in st.session_state:
    st.session_state.userID = None
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "active_chat" not in st.session_state:
    st.session_state.active_chat = None

# Sidebar for user and chat management
with st.sidebar:
    st.header("User & Chats")

    # User registration
    if st.session_state.userID is None:
        st.subheader("Create an Account")
        username = st.text_input("Enter your username")
        if st.button("Register"):
            if username:
                response = requests.post(f"{BACKEND_URL}/register", json={"username": username})
                if response.status_code == 200:
                    st.session_state.userID = response.json()["userID"]
                    st.session_state.chats = {}
                    st.success(f"Account created! Your User ID is: {st.session_state.userID}")
                else:
                    st.error("Failed to register. Please try again.")
            else:
                st.error("Please enter a username.")
    else:
        st.subheader("Your Account")
        st.write(f"User ID: `{st.session_state.userID}`")

        # Create a new chat
        st.subheader("Create a New Chat")
        new_chat_name = st.text_input("Enter a name for the new chat")
        if st.button("Create Chat"):
            if new_chat_name:
                chatID = str(uuid.uuid4())
                st.session_state.chats[chatID] = {"name": new_chat_name, "messages": []}
                st.session_state.active_chat = chatID
                st.success(f"Chat '{new_chat_name}' created!")
            else:
                st.error("Please enter a chat name.")

        # List all chats
        st.subheader("Your Chats")
        for chatID, chat_data in st.session_state.chats.items():
            if st.button(chat_data["name"], key=chatID):
                st.session_state.active_chat = chatID

# Main chat interface
if st.session_state.userID:
    if st.session_state.active_chat:
        st.header(st.session_state.chats[st.session_state.active_chat]["name"])

        # Upload PDFs
        st.subheader("Upload PDFs")
        uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
        if uploaded_files and st.button("Upload and Embed"):
            files = [("files", (file.name, file.getvalue(), "application/pdf")) for file in uploaded_files]
            response = requests.post(f"{BACKEND_URL}/upload", files=files)
            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error(f"Failed to upload PDFs: {response.json()['detail']}")

        # Display chat messages
        chat_messages = st.session_state.chats[st.session_state.active_chat]["messages"]
        for message in chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input for new message
        user_input = st.chat_input("Type your question here...")
        if user_input:
            # Add user message to chat
            st.session_state.chats[st.session_state.active_chat]["messages"].append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # Call FastAPI backend to get the bot's response
            try:
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={
                        "userID": st.session_state.userID,
                        "chatID": st.session_state.active_chat,
                        "question": user_input
                    }
                )
                if response.status_code == 200:
                    result = response.json()
                    # Add bot's response to chat
                    st.session_state.chats[st.session_state.active_chat]["messages"].append({
                        "role": "assistant",
                        "content": result["answer"],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    # Rerun to update the chat interface
                    st.rerun()
                else:
                    st.error(f"Error: {response.json()['detail']}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.info("Please create or select a chat to start.")
else:
    st.info("Please create an account to start using the chatbot.")

# # Run the Streamlit app
# if __name__ == "__main__":
#     st.run("streamlit_app.py")