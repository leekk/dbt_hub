import streamlit as st
import requests
from difflib import get_close_matches

# DBT DATABASE
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

# CONVERSATIONAL RESPONSES
def get_dbt_response(user_input):
    user_input = user_input.lower()
    
    if any(greet in user_input for greet in ["hi","hello","hey"]):
        return "Hello!"
    
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
        #API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
        API_URL = "https://api-inference.huggingface.co/models/HuggingFaceTB/SmolLM3-3B"
        headers = {"Authorization": f"Bearer {st.secrets['HF_API_TOKEN']}"} 


        prompt = f"""You're a DBT therapist. The user said "{user_input}". 
        You reply warmly in 1-2 sentences. If DBT related, name the skill."""

        
        #response = requests.post(API_URL, json={"inputs": prompt}, timeout=3).json()
        #return response['generated_text'].split(".")[0] + " 🌱"
    #except:
        #return "Let's focus on DBT skills. Try asking about mindfulness or distress tolerance!"

        response = requests.post(API_URL, json={"inputs": prompt}, timeout=5)
        response_json = response.json()

        st.write("RAW RESPONSE:", response_json)

        if 'generated_text' in response_json:
            return response_json['generated_text'].split(".")[0] + " 🌱"
        else:
            return "I'm here for you! Maybe we can talk about radical acceptance or emotion regulation? 🌿"

    except Exception as e:
        st.write("AI Fallback error:", e)
        return "Let's focus on DBT skills. Try asking about mindfulness or distress tolerance!"

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
