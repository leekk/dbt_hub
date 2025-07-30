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

import streamlit as st
from difflib import get_close_matches
import requests
import random

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
    # ... (keep your other skill definitions)
}

# More varied fallback responses
GENERAL_RESPONSES = [
    "I hear you. Tell me more about what's on your mind.",
    "That's interesting. How does that make you feel?",
    "I'm listening. Would you like to explore this further?",
    "Thanks for sharing that. What else is coming up for you?"
]

def generate_ai_response(user_input: str) -> str:
    """Generate a more natural response using AI"""
    try:
        API_URL = "https://api-inference.huggingface.co/models/HuggingFaceTB/SmolLM3-3B"
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        
        prompt = f"""You're a compassionate DBT therapist. The client says: "{user_input}"
        
        Respond naturally while:
        1. Validating their experience
        2. Keeping it conversational
        3. Optionally suggesting a DBT skill if relevant
        Respond in 1-2 short sentences."""
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=5
        )
        
        if response.status_code == 200:
            generated = response.json().get('generated_text', '').strip()
            # Add a fallback if the generated text is empty
            return generated if generated else random.choice(GENERAL_RESPONSES)
        
        return random.choice(GENERAL_RESPONSES)
        
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return random.choice(GENERAL_RESPONSES)

def get_dbt_response(user_input: str) -> str:
    """Get response with priority: DBT skills > AI > fallback"""
    user_input = user_input.lower()
    
    # 1. Check for greetings
    if any(greet in user_input for greet in ["hi","hello","hey"]):
        return "Hello! I'm here to help with DBT skills. How can I support you today?"
    
    # 2. Check for exact DBT keywords
    for skill, data in DBT_SKILLS.items():
        if any(keyword in user_input for keyword in data["keywords"]):
            return data["response"]
    
    # 3. Check for similar DBT keywords
    all_keywords = [kw for skill in DBT_SKILLS.values() for kw in skill["keywords"]]
    if matches := get_close_matches(user_input, all_keywords, n=1, cutoff=0.6):
        for skill, data in DBT_SKILLS.items():
            if matches[0] in data["keywords"]:
                return data["response"]
    
    # 4. Generate AI response for everything else
    return generate_ai_response(user_input)

# ... (rest of your UI code remains the same)

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

