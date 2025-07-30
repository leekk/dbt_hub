import streamlit as st
from difflib import get_close_matches
import requests
import random
from typing import Optional

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
        "response": """it's normal to feel this way. Would you like to go through your feelings together?"""
    }
}

DBT_FALLBACK_RESPONSES = [
    "Let's practice the 'Observe' skill - what are you noticing right now?",
    "This sounds like a good moment for some paced breathing. Want to try it with me?",
    "I'm here with you. Would describing your feelings help right now?",
    "Remember the 'STOP' skill: Stop, Take a step back, Observe, Proceed mindfully"
]

def get_ai_fallback_response(user_input: str) -> str:
    """Get a DBT-focused response from HuggingFace API"""
    try:
        API_URL = "https://api-inference.huggingface.co/models/HuggingFaceTB/SmolLM3-3B"
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        
        prompt = f"""As a DBT therapist, respond to this client statement:
        Client: "{user_input}"
        
        Respond with:
        1. Brief validation (1 sentence)
        2. One relevant DBT skill suggestion
        3. Open-ended question
        Keep it under 3 sentences total."""
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json().get('generated_text', 
                  "I hear you. Let's try some mindfulness exercises together. 🌿")
        
        return random.choice(DBT_FALLBACK_RESPONSES)
        
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return random.choice(DBT_FALLBACK_RESPONSES)

def get_dbt_response(user_input: str) -> str:
    """Get appropriate DBT response based on user input"""
    user_input = user_input.lower()
    
    # Greetings
    if any(greet in user_input for greet in ["hi","hello","hey"]):
        return "Hello! I'm here to help with DBT skills. How can I support you today?"
    
    # Exact keyword matching
    for skill, data in DBT_SKILLS.items():
        if any(keyword in user_input for keyword in data["keywords"]):
            return data["response"]
    
    # Fuzzy matching
    all_keywords = [kw for skill in DBT_SKILLS.values() for kw in skill["keywords"]]
    if matches := get_close_matches(user_input, all_keywords, n=1, cutoff=0.6):
        for skill, data in DBT_SKILLS.items():
            if matches[0] in data["keywords"]:
                return data["response"]
    
    # AI fallback
    return get_ai_fallback_response(user_input)

# BELOW IS THE UI
st.set_page_config(page_title="Therapy Hub", page_icon="🐀")

# Custom styling
st.markdown("""
<style>
    [data-testid="stChatMessage"] {
        padding: 15px;
        border-radius: 12px;
    }
    [data-testid="stChatMessage"][aria-label*="assistant"] {
        background-color: #FFA500;
    }
    .stButton button {
        background: #FFA500 !important;
        border: 1px solid #C76E00 !important;
    }
    [data-testid="stAppViewContainer"] > .main {
    background-color: #ADD8E6; /* Light blue example */
    }
    </style>
""", unsafe_allow_html=True)

# initializing chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi there!"}]

# Display chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

cols = st.columns(3)
if cols[0].button("I want to learn"):
    st.session_state.messages.append({"role": "assistant", "content": """Do you know what you would like to learn? 
I can briefly review any area that interets you, just give me the keywords!"""})
if cols[1].button("I want to talk"):
    st.session_state.messages.append({"role": "assistant", "content": """Go ahead, let me know if you would like advice, 
    some skills, a quick solution or simply a friendly ear!"""})
if cols[2].button("I don't want to solve my problem but I should probably be solving my problem rn"):
    st.session_state.messages.append({"role": "assistant", "content": """it do be like that"""})

# User input
if prompt := st.chat_input("Ask about DBT skills..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response = get_dbt_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

