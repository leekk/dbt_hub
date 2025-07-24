import streamlit as st
import requests
from difflib import get_close_matches

# ====== ENHANCED DBT SKILLS DATABASE ======
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
    }
}

# ====== CONVERSATIONAL AI RESPONSE ======
def get_dbt_response(user_input):
    user_input = user_input.lower()
    
    # 1. Handle greetings naturally
    if any(greet in user_input for greet in ["hi","hello","hey"]):
        return "Hello! 😊 I'm your DBT coach. Try asking about skills like TIPP or mindfulness!"
    
    # 2. Check for exact matches
    for skill, data in DBT_SKILLS.items():
        if any(keyword in user_input for keyword in data["keywords"]):
            return data["response"]
    
    # 3. Fuzzy matching
    all_keywords = [kw for skill in DBT_SKILLS.values() for kw in skill["keywords"]]
    matches = get_close_matches(user_input, all_keywords, n=1, cutoff=0.6)
    if matches:
        for skill, data in DBT_SKILLS.items():
            if matches[0] in data["keywords"]:
                return data["response"]
    
    # 4. AI Fallback (with DBT context)
    try:
        API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
        prompt = f"""You're a DBT therapist. Respond warmly in 1-2 sentences to:
        "{user_input}"
        - If DBT-relevant, mention a skill
        - Otherwise, gently guide back to DBT, try a different sentence at each time"""
        
        response = requests.post(API_URL, json={"inputs": prompt}, timeout=3).json()
        return response['generated_text'].split(".")[0] + " 🌱"
    except:
        return "Let's focus on DBT skills. Try asking about mindfulness or distress tolerance!"

# ====== STREAMLIT UI (WITH YOUR LOVED FORMATTING) ======
st.set_page_config(page_title="DBT Coach", page_icon="🧠")

# Custom styling
st.markdown("""
<style>
    [data-testid="stChatMessage"] {
        padding: 15px;
        border-radius: 12px;
    }
    [data-testid="stChatMessage"][aria-label*="assistant"] {
        background-color: #f0f7ff;
    }
    .stButton button {
        background: #f0f7ff !important;
        border: 1px solid #d0e0ff !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your DBT coach. 🌸 How can I help you today?"}]

# Display chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Skill buttons (your favorite feature!)
cols = st.columns(3)
if cols[0].button("🚨 Crisis Help"):
    st.session_state.messages.append({"role": "user", "content": "TIPP skills"})
if cols[1].button("🧠 Mindfulness"):
    st.session_state.messages.append({"role": "user", "content": "Mindfulness"})
if cols[2].button("😊 Emotion Help"):
    st.session_state.messages.append({"role": "user", "content": "Emotion regulation"})

# User input
if prompt := st.chat_input("Ask about DBT skills..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response = get_dbt_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
