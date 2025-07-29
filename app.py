import streamlit as st
from huggingface_hub import InferenceClient
import os
import time
from datetime import datetime

import streamlit as st
st.write("## Secret Injection Test")

if hasattr(st, "secrets"):
    st.write("Secrets object exists")
    if "HF_TOKEN" in st.secrets:
        st.success(f"✅ Token found: {st.secrets['HF_TOKEN'][:8]}...")
    else:
        st.error("❌ HF_TOKEN missing in st.secrets")
        st.write("Actual secrets:", st.secrets)
else:
    st.error("❌ st.secrets doesn't exist (platform failure)")

# ======================
# CONSTANTS
# ======================
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

# ======================
# BULLETPROOF INITIALIZATION
# ======================
st.set_page_config(
    page_title="DBT Therapy Assistant",
    page_icon="🧠",
    layout="wide"
)

# Debug header
st.sidebar.title("Debug Console")
st.sidebar.write(f"Last check: {datetime.now().strftime('%H:%M:%S')}")

# ======================
# TOKEN VALIDATION
# ======================
try:
    # 1. DEMAND the token (no .get() - fails fast if missing)
    token = st.secrets["HF_TOKEN"]
    
    # 2. Validate format
    if not isinstance(token, str) or not token.startswith("hf_"):
        st.error(f"""
        ❌ Invalid token format:
        - Type: {type(token)}
        - Value: {token[:10] + '...' if token else 'None'}
        - Must start with 'hf_'
        """)
        st.stop()
    
    # 3. Masked display for verification
    st.sidebar.success(f"✅ Token loaded: {token[:8]}...{token[-4:]}")
    
except KeyError:
    st.error("""
    ❌ Secret 'HF_TOKEN' not found in st.secrets.
    Verify your Streamlit Secrets:
    1. Go to [share.streamlit.io](https://share.streamlit.io/)
    2. App → Settings → Secrets
    3. Must contain EXACTLY:
       ```toml
       [secrets]
       HF_TOKEN = "hf_your_token_here"  # Quotes required
       ```
    """)
    st.stop()

# ======================
# CLIENT INITIALIZATION
# ======================
try:
    client = InferenceClient(
        token=token,
        model=MODEL_NAME,
        timeout=30,
        server_url="https://api-inference.huggingface.co/models"  # Force correct endpoint
    )
    st.sidebar.success("✅ Inference client initialized")
except Exception as e:
    st.error(f"""
    ❌ Client initialization failed:
    {str(e)}
    
    Common fixes:
    1. Regenerate your HF token
    2. Check model name: {MODEL_NAME}
    3. Wait 5 mins and redeploy
    """)
    st.stop()

# ======================
# CORE FUNCTIONALITY
# ======================
def generate_dbt_response(user_input: str) -> str:
    """Generate therapist response with robust error handling"""
    prompt = f"""Act as a DBT therapist. Respond to: {user_input}
    Format:
    1. [Empathy statement]
    2. [Skill suggestion]
    3. Worksheet: [Name] - [Description]"""
    
    try:
        time.sleep(1.5)  # Rate limit protection
        response = client.text_generation(
            prompt=prompt,
            max_new_tokens=150,
            temperature=0.7,
            do_sample=True
        )
        return response
    except Exception as e:
        return f"""⚠️ System Busy - Sample Response:
        1. I hear you're feeling distressed
        2. Try TIPP skills (Temperature, Intense exercise)
        3. Worksheet: Emotion Regulation - Changing Responses
        [Error: {str(e)}]"""

# ======================
# UI COMPONENTS
# ======================
st.title("DBT Therapy Assistant")
st.caption("Note: AI-generated suggestions, not professional medical advice")

if user_input := st.chat_input("How can I help today?"):
    with st.spinner("🧠 Processing..."):
        response = generate_dbt_response(user_input)
    
    with st.chat_message("assistant"):
        st.write(response)
        st.caption("Always consult a human therapist for clinical care")

# ======================
# DEBUG FOOTER
# ======================
with st.sidebar.expander("Technical Details"):
    st.write("Model:", MODEL_NAME)
    st.write("Token source:", "Streamlit Secrets")
    st.write("Environment keys:", [k for k in os.environ if "HF_" in k])

'''
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

        st.write("HF token begins with:", st.secrets['HF_API_TOKEN'][:10] + "********")


        prompt = f"""You're a DBT therapist. The user said "{user_input}". 
        You reply warmly in 1-2 sentences. If DBT related, name the skill."""

       
        test_url = "https://api-inference.huggingface.co/models/HuggingFaceTB/SmolLM3-3B"

        test_response = requests.get(test_url, headers=headers)
        st.write("HF test response:", test_response.status_code, test_response.text)

        
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
'''
