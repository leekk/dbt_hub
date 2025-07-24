import streamlit as st
import requests

# Hugging Face model and your API token
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"
API_TOKEN = "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"  # 🔁 Replace with your token

headers = {"Authorization": f"Bearer {API_TOKEN}"}

def query_hf(payload):
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Title
st.title("🧠 DBT Skills Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Input box
user_input = st.text_input("You:", key="input")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Format prompt
    prompt = (
        "You are a supportive therapist who teaches Dialectical Behavior Therapy (DBT) skills "
        "in a friendly, conversational tone. Help the user understand DBT one step at a time.\n\n"
        f"User: {user_input}\nAssistant:"
    )

    # Query model
    output = query_hf({
        "inputs": prompt,
        "parameters": {"max_new_tokens": 150}
    })

    # Debug: Show raw output (optional)
    # st.write("Raw output:", output)

    # Handle response safely
    try:
        if isinstance(output, list) and "generated_text" in output[0]:
            bot_reply = output[0]["generated_text"].split("Assistant:", 1)[-1].strip()
        elif isinstance(output, dict) and "error" in output:
            bot_reply = f"⚠️ API error: {output['error']}"
        else:
            bot_reply = "🤖 Sorry, I didn't get a valid response."
    except Exception as e:
        bot_reply = f"⚠️ Unexpected error: {e}"

    # Save bot response
    st.session_state.messages.append({"role": "bot", "content": bot_reply})

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")
