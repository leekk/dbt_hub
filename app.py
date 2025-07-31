import streamlit as st
from difflib import get_close_matches
import requests
import random
import time
import json

# -------------------- DATABASE --------------------
DBT_SKILLS = {
    "distress": {
        "keywords": ["overwhelmed", "panic", "crisis", "tipp", "stress"],
        "response": """**🚨 TIPP Skills (Crisis Survival):**
1. 🌡️ **Temperature** - Splash cold water on your face
2. 🏃 **Intense Exercise** - 1 minute of vigorous activity
3. 🌬️ **Paced Breathing** - Inhale 4s → Hold 4s → Exhale 6s
4. 💪 **Paired Muscle Relaxation** - Tense then release muscles"""
    },
    "mindful": {
        "keywords": ["present", "focus", "mindful", "grounding"],
        "response": """**🧠 Mindfulness WHAT Skills:**
1. 👀 **Observe** - Notice without judgment
2. 📝 **Describe** - Put words to your experience
3. 🎯 **Participate** - Fully engage in the moment"""
    },
    "dysphoric": {
        "keywords": ["sad", "upset", "miserable", "down"], 
        "response": """It's normal to feel this way. Would you like to go through your feelings together?"""
    }
}

# DEBUGGING SETUP
def show_debug_info():
    st.sidebar.markdown("### 🔍 DEBUG PANEL")
    st.sidebar.write("**Token exists:**", "HF_TOKEN" in st.secrets)
    if "HF_TOKEN" in st.secrets:
        st.sidebar.write("**Token starts with:**", st.secrets["HF_TOKEN"][:4] + "..." + st.secrets["HF_TOKEN"][-4:])
    else:
        st.sidebar.error("HF_TOKEN not found in secrets!")

# -------------------- CONVO --------------------
def generate_ai_response(user_input: str, conversation_history: list) -> str:
    """Generate responses using Mistral-7B-Instruct-v0.3"""
    try:
        API_URL = "https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3"
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        
        # Build a simple text prompt (not JSON)
        history_text = "\n".join(
            f"{msg['role']}: {msg['content']}" 
            for msg in conversation_history[-3:]  # Last 3 messages
        )
        prompt = f"""You are a compassionate DBT therapist. Respond to the client in 1-2 sentences.
        
        Conversation history:
        {history_text}
        
        Client: {user_input}
        Therapist:"""
        
        # DEBUG: Show the prompt
        st.sidebar.code(f"Prompt:\n{prompt}")
        st.sidebar.write("Sending text prompt to:", API_URL)

        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": prompt,  # Send as simple text input
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.7,
                    "do_sample": True
                }
            },
            timeout=15
        )

        # DEBUG: Show full response info
        st.sidebar.write("Status code:", response.status_code)
        st.sidebar.write("Response text:", response.text[:500] + "...")
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                # Extract generated text
                generated = result[0].get('generated_text', '')
                
                # Remove the original prompt from the response
                if prompt in generated:
                    generated = generated.replace(prompt, "")
                    
                return generated.strip() or "I'm here for you. What would you like to talk about?"
        
        return "Let's focus on DBT skills. Try asking about mindfulness or distress tolerance."

    except Exception as e:
        st.sidebar.error(f"Error: {str(e)}")
        return random.choice(GENERAL_RESPONSES)

GENERAL_RESPONSES = [
    "I hear you. Tell me more about that.",
    "That's interesting. What else comes to mind?",
    "Thanks for sharing. How does that relate to how you're feeling?",
    "I'm following along. Would you like to explore this further?",
    "Let's stay with that feeling for a moment. What do you notice?",
]

def get_dbt_response(user_input: str, conversation_history: list) -> str:
    """Get response with priority: DBT skills > AI generation"""
    user_input_lower = user_input.lower().strip()
    
    # 1. Strict greeting check (only at conversation start)
    if len(conversation_history) <= 1:
        if any(user_input_lower == greet for greet in ["hi", "hello", "hey"]):
            return "Hello! I'm here to help with DBT skills. How can I support you today?"
    
    # 2. Check for exact DBT keywords
    for skill, data in DBT_SKILLS.items():
        if any(f" {keyword} " in f" {user_input_lower} " for keyword in data["keywords"]):
            return data["response"]
    
    # 3. Fuzzy matching for DBT terms
    all_keywords = [kw for skill in DBT_SKILLS.values() for kw in skill["keywords"]]
    if matches := get_close_matches(user_input_lower, all_keywords, n=1, cutoff=0.6):
        for skill, data in DBT_SKILLS.items():
            if matches[0] in data["keywords"]:
                return data["response"]
    
    # 4. Generate AI response
    return generate_ai_response(user_input, conversation_history)

# -------------------- UI --------------------
st.set_page_config(page_title="DBT Hub", page_icon="🐀", layout="wide")
st.markdown("""<style>/* Your existing CSS */</style>""", unsafe_allow_html=True)

st.title("This is a title")  # Big title
st.header("This is a header")  # Medium header
st.subheader("This is a subheader")  # Smaller header
st.text("This is plain text")  # Fixed-width text
st.markdown("**This** is *markdown*")  # Supports Markdown
st.write("This works with almost anything")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! I'm your DBT companion. How can I support you today?"}
    ]

# Display chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
if prompt := st.chat_input("Share your thoughts..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.spinner("Thinking..."):
        response = get_dbt_response(prompt, st.session_state.messages)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

