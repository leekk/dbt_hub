import streamlit as st
from huggingface_hub import InferenceClient

API_TOKEN = st.secrets["HF_API_TOKEN"]
st.write("Token starts with hf_:", API_TOKEN.startswith("hf_"))

client = InferenceClient(model="HuggingFaceTB/SmolLM3-3B", token=API_TOKEN)
response = client.text_generation("Hello", max_new_tokens=10)
st.write(response)

"""import streamlit as st
from huggingface_hub import InferenceClient

# Replace with your real Hugging Face API token (keep it secret!)
API_TOKEN = st.secrets["HF_API_TOKEN"]

# Initialize the Hugging Face Inference client for SmolLM3-3B
client = InferenceClient(model="HuggingFaceTB/SmolLM3-3B", token=API_TOKEN)

st.title("🧠 DBT Skills Chatbot with SmolLM3-3B")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# User input box
user_input = st.text_input("You:", key="input")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Craft the prompt to guide the model toward DBT skills teaching
    prompt = (
        "You are a supportive therapist teaching Dialectical Behavior Therapy (DBT) skills "
        "in a friendly and easy-to-understand way. "
        "Answer step-by-step and keep your tone encouraging.\n\n"
        f"User: {user_input}\nAssistant:"
    )

    try:
        # Generate a response from the model with a token limit
        outputs = client.text_generation(prompt, max_new_tokens=150)
        if outputs and isinstance(outputs, list):
            bot_reply = outputs[0].strip()
        else:
            bot_reply = "🤖 Sorry, I didn't get a valid response."
    except Exception as e:
        bot_reply = f"⚠️ API error: {e}"

    # Save bot reply to session state
    st.session_state.messages.append({"role": "bot", "content": bot_reply})

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")"""
