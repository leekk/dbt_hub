import streamlit as st
from huggingface_hub import InferenceClient

st.title("🧠 DBT Skills Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.text_input("You:", key="input")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    prompt = (
        "You are a supportive therapist teaching Dialectical Behavior Therapy (DBT) skills "
        "in a conversational, friendly tone. Answer step-by-step.\n\n"
        f"User: {user_input}\nAssistant:"
    )

    client = InferenceClient(token="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")
    try:
        output = client.text_generation(prompt, max_new_tokens=150)
    except Exception as e:
        bot_reply = f"⚠️ API error: {e}"
    else:
        # output.response is a list of strings (responses)
        if output and isinstance(output, list):
            bot_reply = output[0].strip() 
        else:
            bot_reply = "🤖 Sorry, no valid response."

    st.session_state.messages.append({"role": "bot", "content": bot_reply})

# Display chat
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")
