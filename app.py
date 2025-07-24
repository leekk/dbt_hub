import streamlit as st
import requests

st.title("🧠 DBT Skills Chatbot")
st.caption("a tool for learning DBT skills")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm here to help you with DBT skills. What would you like to learn about today?"}]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
if prompt := st.chat_input("Your message"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Prepare the prompt with instructions
    full_prompt = f"""Act as a DBT therapist. Respond to this in a supportive way, teaching DBT skills in simple steps. Keep it under 100 words.
    
    User: {prompt}
    Therapist:"""
    
    # Use Hugging Face's free inference API (no token needed for some models)
    try:
        API_URL = "https://api-inference.huggingface.co/models/gpt2"
        response = requests.post(API_URL, json={"inputs": full_prompt})
        bot_reply = response.json()[0]['generated_text'].split("Therapist:")[-1].strip()
    except:
        # Fallback to rule-based responses if API fails
        lower_prompt = prompt.lower()
        if any(word in lower_prompt for word in ["distress", "crisis", "upset"]):
            bot_reply = """Try TIPP skills:
1. Temperature (cold water on face)
2. Intense exercise (1 minute)
3. Paced breathing (4-4-6)
4. Paired muscle relaxation"""
        elif any(word in lower_prompt for word in ["mindfulness", "present"]):
            bot_reply = "Mindfulness means observing, describing, and participating in the present moment without judgment."
        else:
            bot_reply = "I'm here to help with DBT skills. Could you tell me more about what you're working on?"
    
    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    st.chat_message("assistant").write(bot_reply)

st.markdown("""
<style>
    .stChatMessage {
        font-family: 'Arial', sans-serif;
    }
    [data-testid="stChatMessage"] {
        padding: 12px;
        border-radius: 10px;
    }
    .assistant-message {
        background-color: #f0f7ff;
    }
</style>
""", unsafe_allow_html=True)
