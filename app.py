import streamlit as st
import requests

# Hugging Face settings
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
headers = {"Authorization": f"Bearer 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"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

st.set_page_config(page_title="DBT Chatbot", page_icon="💬")

st.title("💬 DBT Chatbot")
st.write("A supportive AI to help you practice DBT skills.")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.text_input("You:", key="input")

if user_input:
    st.session_state.chat_history.append(("You", user_input))

    prompt = f"""
    You are a compassionate DBT therapist. Respond to the user with helpful DBT skills, based on the following message:

    {user_input}
    """

    with st.spinner("Thinking..."):
        output = query({
            "inputs": prompt,
            "parameters": {"max_new_tokens": 150}
        })

        bot_reply = output[0]["generated_text"].split(":", 1)[-1].strip()
        st.session_state.chat_history.append(("DBT-Bot", bot_reply))

# Display chat
for sender, msg in st.session_state.chat_history:
    st.markdown(f"**{sender}:** {msg}")
