import streamlit as st
from huggingface_hub import InferenceClient
import traceback

# Get your Hugging Face API token from Streamlit secrets
API_TOKEN = st.secrets["HF_API_TOKEN"]

# Initialize the Hugging Face Inference client with GPT-2 (publicly supported)
client = InferenceClient(model="gpt2", token=API_TOKEN)

st.title("🧠 DBT Skills Chatbot with GPT-2")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# User input box
user_input = st.text_input("You:", key="input")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Prepare the prompt to guide the chatbot's style and content
    prompt = (
        "You are a supportive therapist teaching Dialectical Behavior Therapy (DBT) skills "
        "in a friendly and easy-to-understand way. "
        "Answer step-by-step and keep your tone encouraging.\n\n"
        f"User: {user_input}\nAssistant:"
    )

    try:
        outputs = client.text_generation(prompt, max_new_tokens=150)
        if outputs and isinstance(outputs, list):
            bot_reply = outputs[0]["generated_text"].strip()
        else:
            bot_reply = "🤖 Sorry, I didn't get a valid response."
    except Exception as e:
        # Capture full traceback for debugging
        error_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
        bot_reply = f"⚠️ API error:\n```\n{error_message}\n```"

    st.session_state.messages.append({"role": "bot", "content": bot_reply})

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")
