import streamlit as st
from difflib import get_close_matches
import requests
import random
import time
import json
# I'm having heart palpations rn haha
import os
from huggingface_hub import InferenceClient

# -------------------- TRYNG AI HERE --------------------
os.environ["HF_TOKEN"] = st.secrets['HF_TOKEN']
st.set_page_config(page_title="DBT Hub", page_icon="🐀", layout="wide")

@st.cache_resource
def get_client():
    return InferenceClient(
        provider="hf-inference",
        api_key=os.environ["HF_TOKEN"]
    )
    
client = get_client()

# -------------------- SKILLS DATABASE --------------------
DBT_SKILLS = {
    "mindfulness": {
        "keywords": ["mindful", "present moment", "observe"],
        "response": "Let's practice mindfulness. Try focusing on your breath for 60 seconds..."
    },
    "distress_tolerance": {
        "keywords": ["crisis", "distress", "urge"],
        "response": "In moments of distress, try the TIPP skill..."
    }
}
# -----------------------------------------------------------
# general fallback responses
GENERAL_RESPONSES = [
    "I hear you. Tell me more about that.",
    "That's interesting. What else comes to mind?",
    "Thanks for sharing. How does that relate to how you're feeling?",
    "I'm following along. Would you like to explore this further?",
    "Let's stay with that feeling for a moment. What do you notice?",
]

# -----------------------------------------------------------
def generate_response(prompt: str, history: list) -> str:
    """Generate AI response with guided personality"""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a compassionate Dialectical Behavior Therapy (DBT) coach."
                "You are a tool to teach DBT skills. When the user brings up a struggle,"
                "you should recognize the pattern in the DBT and provide brief information"
                "on the corresponding skill the user should refer to"
                "Your responses should:\n"
                "- sentence lengths can vary depending on the engagement of the user\n"
                "- Use simple, empathetic language\n"
                "- Focus on DBT skills when relevant\n"
                "- Never give medical advice\n"
                "- Ask open-ended questions to encourage reflection\n"
                'Example: "I hear you\'re feeling anxious. Would practicing paced breathing together help?"'
            )
        },
        *[{"role": m["role"], "content": m["content"]} for m in history]
    ]
    
    completion = client.chat.completions.create(
        model="HuggingFaceTB/SmolLM3-3B",
        messages=messages
    )
    return completion.choices[0].message.content

def get_dbt_response(user_input: str, history: list) -> str:
    """Get response with priority: DBT skills > AI generation"""
    user_input = user_input.lower()
    
    # Check for DBT keywords
    for skill, data in DBT_SKILLS.items():
        if any(keyword in user_input for keyword in data["keywords"]):
            return data["response"]
    
    # Generate AI response if no DBT match
    return generate_response(user_input, history)


# -----------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Chat", "Resources", "About"])
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your DBT companion. How can I help?"}
        ]

    # Display chat history
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # User input
    if prompt := st.chat_input("How are you feeling today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        with st.spinner("Thinking..."):
            response = get_dbt_response(prompt, st.session_state.messages)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)

with tab2:
    st.write("DBT resources and exercises will appear here")

with tab3:
    st.write("About this app and contact information")

# -------------------- CONVO --------------------
with st.sidebar:
    st.header("DBT Skills Quick Access")
    with st.expander("Mindfulness Exercises"):
        st.write("1. 5-4-3-2-1 Grounding Technique...")
    with st.expander("Distress Tolerance"):
        st.write("TIPP Skill: Temperature, Intense exercise...")
