import streamlit as st
from huggingface_hub import InferenceClient

API_TOKEN = st.secrets["HF_API_TOKEN"]
client = InferenceClient(model="gpt2", token=API_TOKEN)

st.title("🧠 DBT Skills Chatbot with GPT-2")

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.text_input("You:", key="input")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
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
        bot_reply = f"⚠️ API error: {str(e)}"

    st.session_state.messages.append({"role": "bot", "content": bot_reply})

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")
