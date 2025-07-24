import streamlit as st
from transformers import pipeline, set_seed

# Set up the app
st.title("🧠 DBT Skills Chatbot")
st.caption("A free, no-installation-required chatbot for DBT skills")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "bot", "content": "Hello! I'm here to help you with DBT skills. What would you like to learn about today?"}]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
if prompt := st.chat_input("Your message"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Prepare the prompt with instructions
    full_prompt = f"""You are a supportive therapist teaching Dialectical Behavior Therapy (DBT) skills.
Respond in a friendly, easy-to-understand way. Break down concepts into simple steps.
Keep responses under 200 words.

User: {prompt}
Therapist:"""
    
    # Use a free model (small enough to run without GPU)
    try:
        generator = pipeline('text-generation', model='gpt2')
        response = generator(full_prompt, max_length=200, do_sample=True, temperature=0.7)
        bot_reply = response[0]['generated_text'].split("Therapist:")[-1].strip()
    except Exception as e:
        bot_reply = f"Sorry, I encountered an error: {str(e)}"
    
    # Add bot response to chat history
    st.session_state.messages.append({"role": "bot", "content": bot_reply})
    st.chat_message("bot").write(bot_reply)
