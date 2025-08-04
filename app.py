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
import pandas as pd

import pytz
#tz = pytz.timezone("America/Toronto")

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
    
    if "editing_event_id" not in st.session_state:
        st.session_state.editing_event_id = None
    if "new_label" not in st.session_state:
        st.session_state.new_label = ""

    # Calendar config
    calendar_options = {
        "editable": True,
        "selectable": True,
        "selectMirror": True,
        "selectHelper": True,
        "selectOverlap": True,
        "slotDuration": "00:15:00",
        "slotMinTime": " ",
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
        .fc-entry-event {
            background-color: white !important;
            color: black !important;
            border-color: white !important;
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
        # Handle calendar interactions
        if calendar_output and calendar_output.get("dateClick"):
            clicked = calendar_output["dateClick"]
            st.session_state.selected = {
                "start": clicked["date"],
                "end": clicked["date"],
                "allDay": clicked["allDay"]
            }
            st.session_state.editing_event_id = None

        if calendar_output and calendar_output.get("select"):
            selected = calendar_output["select"]
            st.session_state.selected = {
                "start": selected["start"],
                "end": selected["end"],
                "allDay": False
            }
            st.session_state.editing_event_id = None

        if calendar_output and calendar_output.get("eventClick"):
            clicked_event = calendar_output["eventClick"]["event"]
            st.session_state.editing_event_id = clicked_event["id"]
            st.session_state.selected_event = next(
                (e for e in st.session_state.calendar_events if e["id"] == clicked_event["id"]),
                None
            )
            st.rerun()

        # Edit form
        if st.session_state.editing_event_id:
            event_to_edit = next(
                e for e in st.session_state.calendar_events 
                if e["id"] == st.session_state.editing_event_id
            )
            
            with st.form("edit_event_form"):
                st.subheader("Edit Event")
                title = st.text_input("Event Title", value=event_to_edit.get("title", "Untitled Event"))
                
                # Only show color picker if not an entry
                if event_to_edit.get("label") != "Entry":
                    color_options = {
                        "Red": "#FF6C6C",
                        "Orange": "#FFBD45",
                        "Green": "#4CAF50",
                        "Blue": "#2196F3",
                        "Purple": "#9C27B0"
                    }
                    current_color = event_to_edit.get("color", "#4CAF50")
                    color_name = st.selectbox(
                        "Pick a color", 
                        list(color_options.keys()),
                        index=list(color_options.values()).index(current_color) if current_color in color_options.values() else 0
                    )
                    color = color_options[color_name]
                else:
                    color = "#FFFFFF"

                # Label selection with new label option
                label_options = ["Event", "Entry"]
                if st.session_state.new_label:
                    label_options.insert(1, st.session_state.new_label)
                
                current_label = event_to_edit.get("label", "Event")
                label = st.selectbox(
                    "Label",
                    label_options + ["Add new label..."],
                    index=label_options.index(current_label) if current_label in label_options else 0
                )
                
                if label == "Add new label...":
                    new_label = st.text_input("New label name", key="new_label_input")
                    if new_label:
                        st.session_state.new_label = new_label
                        st.rerun()
                    label = st.session_state.new_label

                # Time inputs if not an entry
                if label != "Entry":
                    col1, col2 = st.columns(2)
                    with col1:
                        start_time = st.text_input("Start Time", 
                            value=pd.to_datetime(event_to_edit["start"]).strftime("%H:%M") 
                            if "T" in event_to_edit["start"] else "00:00")
                    with col2:
                        end_time = st.text_input("End Time", 
                            value=pd.to_datetime(event_to_edit["end"]).strftime("%H:%M") 
                            if "T" in event_to_edit["end"] else "00:00")
                details = st.text_area("Details", value=event_to_edit.get("details", ""))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    save_clicked = st.form_submit_button("Save Changes")
                with col2:
                    delete_clicked = st.form_submit_button("Delete")
                with col3:
                    cancel_clicked = st.form_submit_button("Cancel")
                
                if save_clicked:
                    event_to_edit.update({
                        "title": title,
                        "color": color,
                        "label": label,
                        "details": details
                    })
                    if label != "Entry":
                        start_date = event_to_edit["start"].split("T")[0]
                        end_date = event_to_edit["end"].split("T")[0]
                        event_to_edit["start"] = f"{start_date}T{start_time}:00"
                        event_to_edit["end"] = f"{end_date}T{end_time}:00"
                    st.session_state.editing_event_id = None
                    st.rerun()
                
                if delete_clicked:
                    st.session_state.calendar_events = [
                        e for e in st.session_state.calendar_events 
                        if e["id"] != st.session_state.editing_event_id
                    ]
                    st.session_state.editing_event_id = None
                    st.rerun()
                
                if cancel_clicked:
                    st.session_state.editing_event_id = None
                    st.rerun()

        # Add event form
        elif calendar_output and calendar_output.get("select"):
            selected = calendar_output["select"]
            with st.form("add_event_form"):
                st.subheader("Add New Event")
                
                event_type = st.radio("Event Type", ["Regular Event", "Entry"])
                
                title = st.text_input("Event Title", value="Untitled Event")
                
                if event_type == "Regular Event":
                    color_options = {
                        "Red": "#FF6C6C",
                        "Orange": "#FFBD45",
                        "Green": "#4CAF50",
                        "Blue": "#2196F3",
                        "Purple": "#9C27B0"
                    }
                    color_name = st.selectbox("Pick a color", list(color_options.keys()))
                    color = color_options[color_name]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        start_time = st.text_input("Start Time", value=pd.to_datetime(selected["start"]).strftime("%H:%M") if "T" in selected["start"] else "00:00")
                    with col2:
                        end_time = st.text_input("End Time", value=pd.to_datetime(selected["end"]).strftime("%H:%M") if "T" in selected["end"] else "00:00")
                else:
                    color = "#FFFFFF"
                
                # Label selection for new events
                label_options = ["Event", "Entry"]
                if st.session_state.new_label:
                    label_options.insert(1, st.session_state.new_label)
                
                label = st.selectbox(
                    "Label",
                    label_options + ["Add new label..."],
                    index=0
                )
                
                if label == "Add new label...":
                    new_label = st.text_input("New label name", key="new_label_input_add")
                    if new_label:
                        st.session_state.new_label = new_label
                        st.rerun()
                    label = st.session_state.new_label
                
                details = st.text_area("Details")
                
                col1, col2 = st.columns(2)
                with col1:
                    add_clicked = st.form_submit_button("Add")
                with col2:
                    cancel_clicked = st.form_submit_button("Cancel")
                
                if add_clicked:
                    if event_type == "Regular Event":
                        try:
                            # Validate time format
                            datetime.strptime(start_time, "%H:%M")
                            datetime.strptime(end_time, "%H:%M")
                            new_event = {
                                "id": str(uuid.uuid4()),
                                "title": title,
                                "start": f"{selected['start'].split('T')[0]}T{start_time}:00",
                                "end": f"{selected['end'].split('T')[0]}T{end_time}:00",
                                "color": color,
                                "label": label,
                                "details": details
                            }
                            st.session_state.calendar_events.append(new_event)
                            st.rerun()
                        except ValueError:
                            st.error("Please enter time in HH:MM format")
                    else:  # Entry
                        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                        new_event = {
                            "id": str(uuid.uuid4()),
                            "title": title,
                            "start": now,
                            "end": now,
                            "color": "#FFFFFF",
                            "label": "Entry",
                            "details": details,
                            "className": "fc-entry-event"
                        }
                        st.session_state.calendar_events.append(new_event)
                        st.rerun()
                
                if cancel_clicked:
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


