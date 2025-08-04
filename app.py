import streamlit as st
from difflib import get_close_matches
import requests
import random
import time
import json
# I'm having heart palpations rn haha
import os
from huggingface_hub import InferenceClient
from streamlit_calendar import calendar
from datetime import datetime, timedelta
import uuid


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
# I need to take out this part w/out damaging anything
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
                "- if the user poses the question in a forgein language, you reply in that language if you know it\n"
                "- Focus on DBT skills when relevant, give in depth information about DBT skills in layman's terms\n"
                "- Never give medical advice\n"
                "- your name is Prongles but you don't need to give that information unless asked directly.\n"
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
tab1, tab2, tab3, tab4 = st.tabs(["Calendar", "Chat", "Featured", "About"])

# okay so the calendar is the main tab, you enter your ESM + voluntary entries, these entried can have labels

# the chat part is to ask more about the skills ONLY, not where you write your problems smh

with tab1:
    if "calendar_events" not in st.session_state:
        st.session_state.calendar_events = [
            {"id": str(uuid.uuid4()), "title": "Past meeting", "start": "2025-08-01", "end": "2025-08-01", "color": "#FF6C6C"},
            {"id": str(uuid.uuid4()), "title": "Meeting 1", "start": "2025-08-05T13:00:00", "end": "2025-08-05T14:00:00", "color": "#FF6C6C"},
            {"id": str(uuid.uuid4()), "title": "URGE SPIKE", "start": "2025-08-05T16:00:00", "color": "#FFBD45"},
        ]
    
    # Initialize edit mode
    if "edit_event_id" not in st.session_state:
        st.session_state.edit_event_id = None

    # Calendar options and CSS (unchanged)
    calendar_options = {
        "editable": True,
        "selectable": True,
        "selectMirror": True,
        "selectHelper": True,
        "selectOverlap": True,
        "slotDuration": "00:15:00",
        "slotMinTime": "00:00:00",
        "slotMaxTime": "24:00:00",
        "dateClick": True,
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "timeGridDay,timeGridWeek,dayGridMonth",
        },
        "initialView": "dayGridMonth",
        "navLinks": True,
    }

    custom_css = """
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
        .fc-event-past {
            opacity: 0.5;
        }
        .fc-event-time {
            font-style: italic;
        }
    """

    col1, col2 = st.columns([2, 1]) 
    with col1: 
        calendar_output = calendar(
            events=st.session_state.calendar_events,
            options=calendar_options,
            custom_css=custom_css,
            key="calendar"
        )

    with col2:
        # Handle date click (for all-day events)
        if calendar_output and calendar_output.get("dateClick"):
            clicked = calendar_output["dateClick"]
            st.session_state.selected = {
                "start": clicked["date"],
                "end": clicked["date"],
                "allDay": clicked["allDay"]
            }
            st.session_state.edit_event_id = None  # Reset edit mode

        # Handle time slot selection (for timed events)
        if calendar_output and calendar_output.get("select"):
            selected = calendar_output["select"]
            st.session_state.selected = {
                "start": selected["start"],
                "end": selected["end"],
                "allDay": False
            }
            st.session_state.edit_event_id = None  # Reset edit mode

        # Handle event click (for edit/delete)
        if calendar_output and calendar_output.get("eventClick"):
            clicked_event = calendar_output["eventClick"]["event"]
            st.session_state.edit_event_id = clicked_event["id"]
            st.session_state.selected_event = next(
                (e for e in st.session_state.calendar_events if e["id"] == clicked_event["id"]), 
                None
            )

        # Event form (for both add and edit)
        if "selected" in st.session_state or "selected_event" in st.session_state:
            color_options = {
                "Red": "#FF6C6C",
                "Orange": "#FFBD45",
                "Green": "#4CAF50",
                "Blue": "#2196F3",
                "Purple": "#9C27B0"
            }
            
            with st.form("event_form", clear_on_submit=True):
                # Determine if we're in edit mode
                is_edit = st.session_state.edit_event_id is not None
                
                if is_edit:
                    st.subheader("Edit Event")
                    event = st.session_state.selected_event
                    default_title = event.get("title", "")
                    default_color_name = next(
                        (k for k, v in color_options.items() if v == event.get("color", "#4CAF50")), 
                        "Green"
                    )
                    default_label = event.get("label", "Event")
                    default_details = event.get("details", "")
                else:
                    st.subheader("Add New Event")
                    default_title = ""
                    default_color_name = "Green"
                    default_label = "Event"
                    default_details = ""
                
                # Form fields
                title = st.text_input("Event Title", value=default_title)
                color_name = st.selectbox(
                    "Pick a color", 
                    list(color_options.keys()),
                    index=list(color_options.keys()).index(default_color_name)
                )
                color = color_options[color_name]
                
                label = st.selectbox(
                    "Label", 
                    ["Event", "Entry", "Add new label..."],
                    index=0 if not is_edit else ["Event", "Entry", "Add new label..."].index(default_label)
                )
                
                if label == "Add new label...":
                    new_label = st.text_input("New label")
                    if new_label:
                        label = new_label
                
                # Show details field only if label is "Entry" or we're editing an entry
                if label.lower() == "entry" or (is_edit and event.get("label", "").lower() == "entry"):
                    details = st.text_area(
                        "Add details", 
                        value=default_details if is_edit else ""
                    )
                else:
                    details = ""
                
                # Form buttons
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("Save" if is_edit else "Add")
                with col2:
                    if is_edit:
                        if st.form_submit_button("Delete"):
                            st.session_state.calendar_events = [
                                e for e in st.session_state.calendar_events 
                                if e["id"] != st.session_state.edit_event_id
                            ]
                            st.session_state.edit_event_id = None
                            st.rerun()
                
                if submitted:
                    if is_edit:
                        # Update existing event
                        for event in st.session_state.calendar_events:
                            if event["id"] == st.session_state.edit_event_id:
                                event.update({
                                    "title": title,
                                    "color": color,
                                    "label": label,
                                    "details": details
                                })
                                # Update start/end if they were changed (you could add fields for these)
                    else:
                        # Add new event
                        new_event = {
                            "id": str(uuid.uuid4()),
                            "title": title,
                            "start": st.session_state.selected["start"],
                            "end": st.session_state.selected["end"],
                            "color": color,
                            "label": label,
                            "details": details
                        }
                        st.session_state.calendar_events.append(new_event)
                    
                    st.session_state.edit_event_id = None
                    st.rerun()
    

with tab2:
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

with tab3:
    st.write("DBT resources and exercises will appear here")
    st.write("Cute Ghosts on Drinking Straws by Kaboompics.com licensed under CC BY 4.0.")

with tab4:
    st.write("About this app and contact information")
    with st.container(border=True):  # 👈 Creates a bordered container
        col1, col2 = st.columns([1, 4])  # image column smaller than text
        with col1:
            st.image("https://via.placeholder.com/60", width=60)  # small image
        with col2:
            st.markdown("**DBT Skill of the Day**  \nLearn how to use Opposite Action to fight emotional inertia.")
        
    with st.container(border=True):  # 👈 Creates a bordered container
        st.markdown("""
        **DBT zine!**  
        [Check it out!](https://www.reddit.com/r/zines/comments/1m1r9ct/wip_dbt_zine/)
        """)
    with st.container(border=True):  # 👈 Creates a bordered container
        st.markdown("""
        **Will Wood - Marsha, Thankk You for the Dialectics, but I Need You to Leave (Official Lyric Video)**  
        [Listen to it here!](https://www.youtube.com/watch?v=nyIKBT7-a9M&list=RDnyIKBT7-a9M&start_radio=1)
        """)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.header("DBT Skills Quick Access")
    with st.expander("Mindfulness Exercises"):
        st.write("1. 5-4-3-2-1 Grounding Technique...")
    with st.expander("Distress Tolerance"):
        st.write("TIPP Skill: Temperature, Intense exercise...")
        
    col_main, col_right = st.columns([4, 1])  # main content left, "sidebar" right

    with col_main:
        st.markdown("### Main Content Area")
        st.write("This is your regular app content.")

    with col_right:
        st.markdown("### 🛠️ Tools")
        st.button("Action")
        st.markdown("Tip: Breathe in for 4 seconds...")


# -------------------- UI EXTRA(TESTING BGS) --------------------
#st.markdown(
#    """
#    <style>
#    .stApp {
#        background-image: url("https://www.transparenttextures.com/patterns/white-wall-3.png");
#        background-size: cover;
#        background-repeat: no-repeat;
#        background-attachment: fixed;
#    }
#    </style>
#    """,
#    unsafe_allow_html=True
#)

#st.markdown(
#    """
#    <style>
#    section[data-testid="stSidebar"] {
#        background-image: url("https://www.transparenttextures.com/patterns/white-wall-3.png");
#        background-repeat: no-repeat;
#        background-size: cover;
#        background-position: center;
#    }
#    </style>
#    """,
#    unsafe_allow_html=True
#)
# -------------------- CALENDAR N STUFF --------------------

