import streamlit as st
import openai

# Load API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="DBT Check the Facts", page_icon="🧠")
st.title("🧠 DBT: Check the Facts Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": (
            "You are a supportive Dialectical Behavior Therapy (DBT) coach helping the user regulate emotions "
            "using the skill 'Check the Facts'. Ask them step-by-step:\n"
            "1. What emotion they’re feeling,\n"
            "2. What event triggered it,\n"
            "3. What thoughts they had about it,\n"
            "4. Whether those thoughts are supported by evidence or might have alternative explanations,\n"
            "5. Whether their emotional reaction fits the facts and intensity of the event.\n"
            "Stay warm, brief, and non-judgmental. Offer encouragement and positive reinforcement at the end."
        )}
    ]

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("How are you feeling right now?")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Send to OpenAI
    response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=st.session_state.messages,
    temperature=0.7,
)

    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.markdown(reply)
