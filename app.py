import streamlit as st
import requests

# ====== DBT KNOWLEDGE BASE ======
DBT_CONCEPTS = {
    "distress": {
        "keywords": ["crisis", "overwhelmed", "panic", "tipp"],
        "facts": """TIPP stands for Temperature, Intense Exercise, Paced Breathing, and Paired Muscle Relaxation."""
    },
    "mindfulness": {
        "keywords": ["present", "focus", "mindful"],
        "facts": """Mindfulness involves Observe, Describe, and Participate skills."""
    }
}

# ====== AI-ASSISTED RESPONSE GENERATOR ======
def generate_response(user_input):
    # Step 1: Check for DBT concepts
    detected_concept = None
    for concept, data in DBT_CONCEPTS.items():
        if any(keyword in user_input.lower() for keyword in data["keywords"]):
            detected_concept = data["facts"]
            break
    
    # Step 2: Prepare AI prompt with guardrails
    prompt = f"""You are a Dialectical Behavior Therapy (DBT) coach. 
Respond conversationally to this client question while incorporating these DBT facts:
{detected_concept if detected_concept else "Use general DBT principles"}

Client: {user_input}
Coach:"""
    
    # Step 3: Get AI-generated response (free API)
    try:
        API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
        response = requests.post(
            API_URL,
            json={"inputs": prompt},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()['generated_text']
    except:
        pass
    
    # Fallback response
    return "Let me think about how DBT skills could help with that..."

# ====== STREAMLIT CHAT ======
st.title("🧠 Conversational DBT Coach")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your DBT coach. What's on your mind today?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("How can DBT help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response = generate_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

