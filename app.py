import streamlit as st
from difflib import get_close_matches
import requests
import random
import time

# DATABASE
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

# CONVERSATIONAL RESPONSES
def generate_ai_response(user_input: str, conversation_history: list) -> str:
    """Generate AI response using HuggingFace API"""
    try:
        # Switch to a more reliable chat model
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        
        # Build conversation history in instruction format
        conversation = "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}" 
            for msg in conversation_history[-4:]  # Keep last 4 messages for context
        )
        
        prompt = f"""<s>[INST] You are a compassionate DBT therapist. Continue this conversation naturally:
        
{conversation}
User: {user_input}
Therapist: [/INST]"""
        
        # DEBUG
        st.sidebar.write("**Prompt:**", prompt)
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated = result[0].get('generated_text', '').strip()
                # Clean up the response
                if "Therapist:" in generated:
                    generated = generated.split("Therapist:")[-1].strip()
                if "[/INST]" in generated:
                    generated = generated.split("[/INST]")[-1].strip()
                return generated if generated else random.choice(GENERAL_RESPONSES)
        
        st.sidebar.error(f"API Error: {response.status_code} - {response.text[:200]}")
        return random.choice(GENERAL_RESPONSES)
        
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
    
    # DEBUG: Show input analysis
    st.sidebar.write("**Input Analysis**")
    st.sidebar.write(f"Input: '{user_input}'")
    
    # 1. Strict greeting check (only at conversation start)
    if len(conversation_history) <= 1:  # Only first message
        if any(user_input_lower == greet for greet in ["hi", "hello", "hey"]):
            st.sidebar.success("Matched: Greeting")
            return "Hello! I'm here to help with DBT skills. How can I support you today?"
    
    # 2. Check for exact DBT keywords
    matched_skill = None
    for skill, data in DBT_SKILLS.items():
        for keyword in data["keywords"]:
            if f" {keyword} " in f" {user_input_lower} ":
                matched_skill = skill
                break
        if matched_skill:
            break
    
    if matched_skill:
        st.sidebar.success(f"Matched DBT skill: {matched_skill}")
        return DBT_SKILLS[matched_skill]["response"]
    
    # 3. Fuzzy matching for DBT terms
    all_keywords = [kw for skill in DBT_SKILLS.values() for kw in skill["keywords"]]
    if matches := get_close_matches(user_input_lower, all_keywords, n=1, cutoff=0.6):
        st.sidebar.success(f"Fuzzy matched: {matches[0]}")
        for skill, data in DBT_SKILLS.items():
            if matches[0] in data["keywords"]:
                return data["response"]
    
    # 4. Generate AI response
    st.sidebar.info("No keyword match → Using AI generation")
    return generate_ai_response(user_input, conversation_history)

# UI SETUP
st.set_page_config(page_title="Therapy Hub", page_icon="🐀", layout="wide")

# Custom styling
st.markdown("""
<style>
    [data-testid="stChatMessage"] {
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    [data-testid="stChatMessage"][aria-label*="assistant"] {
        background-color: #FFEECC;
        border-left: 4px solid #FFA500;
    }
    [data-testid="stChatMessage"][aria-label*="user"] {
        background-color: #E6F3FF;
        border-left: 4px solid #1E90FF;
    }
    .stButton button {
        background: #FFA500 !important;
        border: 1px solid #C76E00 !important;
        color: white !important;
    }
    .stTextInput input {
        border-radius: 20px !important;
        padding: 10px 15px !important;
    }
    [data-testid="stAppViewContainer"] > .main {
        background-color: #F0F8FF;
    }
    .sidebar .sidebar-content {
        background-color: #FFF8F0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! I'm your DBT companion. How can I support you today?"}
    ]

# Main chat area
st.title("DBT Therapy Companion")
st.caption("A supportive chatbot for Dialectical Behavior Therapy skills")

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Quick buttons
cols = st.columns(3)
if cols[0].button("Learn DBT Skills"):
    st.session_state.messages.append({"role": "assistant", "content": 
        "I can teach you DBT skills! Try asking about: distress tolerance, mindfulness, or emotion regulation."})
if cols[1].button("I'm Feeling Overwhelmed"):
    st.session_state.messages.append({"role": "assistant", "content": DBT_SKILLS["distress"]["response"]})
if cols[2].button("Reset Conversation"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! Let's start fresh. How are you feeling today?"}
    ]

# User input
if prompt := st.chat_input("Share your thoughts or ask about DBT skills..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.spinner("Thinking..."):
        # Add small delay to show spinner
        time.sleep(0.3)
        response = get_dbt_response(prompt, st.session_state.messages)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

