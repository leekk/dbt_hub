import streamlit as st
from difflib import get_close_matches
import requests

# ====== ENHANCED DBT SKILLS DATABASE ======
DBT_SKILLS = {
    "distress": """**🚨 TIPP Skills (Crisis Survival):**
1. 🌡️ **Temperature** - Splash cold water on your face or hold ice
2. 🏃 **Intense Exercise** - 1 minute of jumping jacks/running
3. 🌬️ **Paced Breathing** - Inhale 4s → Hold 4s → Exhale 6s
4. 💪 **Paired Muscle Relaxation** - Tense muscles for 5s then release""",

    "mindful": """**🧠 Mindfulness WHAT Skills:**
1. 👀 **Observe** - "I notice my heart is racing"
2. 📝 **Describe** - "I'm feeling anxious about my exam"
3. 🎯 **Participate** - Fully engage in brushing your teeth""",

    "emotion": """**😊 Emotion Regulation:**
• **PLEASE** (Physical health): Eat/sleep/exercise
• **ABC** (Accumulate positives): Do 1 nice thing daily
• **Opposite Action** - If angry, be kind instead""",

    "dear man": """**🤝 DEAR MAN (Assertiveness):**
D - Describe facts: "When we planned to meet at 8..."
E - Express feelings: "I felt worried when..."
A - Assert needs: "I need us to text if late"
R - Reinforce: "I'd really appreciate this"
M - Mindful (stay focused)
A - Appear confident
N - Negotiate: "What do you think?""",

    "accept": """**✋ Radical Acceptance:**
1. Observe resistance: "I'm fighting this reality"
2. Say: "This is what happened"
3. Imagine accepting it
4. List ways your life would change""",

    "cope": """📝 **Coping Ahead Plan:**
1. Describe triggering situation
2. Choose 2 skills to use
3. Rehearse in your mind
4. Pack a coping kit (photos, quotes, items)"""
}

# ====== SMARTER RESPONSE SYSTEM ======
def get_dbt_response(user_input):
    user_input = user_input.lower()
    
    # Priority phrases (even if mixed with other words)
    priority_phrases = {
        "panic attack": DBT_SKILLS["distress"],
        "can't calm down": DBT_SKILLS["distress"],
        "assertive": DBT_SKILLS["dear man"],
        "mind wandering": DBT_SKILLS["mindful"]
    }
    
    for phrase, response in priority_phrases.items():
        if phrase in user_input:
            return response
    
    # Fuzzy keyword matching
    matches = get_close_matches(user_input, DBT_SKILLS.keys(), n=1, cutoff=0.5)
    if matches:
        return DBT_SKILLS[matches[0]]
    
    # Fallback: Use free API if no match found
    try:
        API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
        response = requests.post(API_URL, 
                               json={"inputs": f"As a DBT therapist, answer briefly: {user_input}"},
                               timeout=3)
        if response.status_code == 200:
            return response.json()['generated_text'].split(".")[0] + " (via DBT skills)"
    except:
        pass
    
    # Final fallback
    skill_list = "\n• ".join([f"**{k.capitalize()}**" for k in DBT_SKILLS.keys()])
    return f"""I can explain these DBT skills:\n\n• {skill_list}\n\nTry: *"How do I use TIPP when overwhelmed?"*"""

# ====== STREAMLIT UI ======
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
    }
</style>
""", unsafe_allow_html=True)

# Quick-access buttons
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your DBT Coach. Ask about skills like **TIPP**, **DEAR MAN**, or **Mindfulness**."}]

# Display chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Skill buttons
cols = st.columns(3)
if cols[0].button("🚨 Crisis Help"):
    st.session_state.messages.append({"role": "user", "content": "TIPP skills"})
if cols[1].button("🧠 Mindfulness"):
    st.session_state.messages.append({"role": "user", "content": "mindfulness"})
if cols[2].button("🤝 Relationships"):
    st.session_state.messages.append({"role": "user", "content": "DEAR MAN"})

# User input
if prompt := st.chat_input("Ask about DBT skills..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response = get_dbt_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
