import streamlit as st

# Your other imports like gsheets here...

# ✨ Injecting the custom CSS for SF Pro Display
st.markdown("""
    <style>
    html, body, [class*="st-"] {
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

# The rest of your app code goes down here...
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="Cloud Planner", page_icon="☁️", layout="centered")
st.title("Moi's Planner")

# --- DATABASE CONNECTION ---
# This connects to the URL you will provide in the "Secrets" section later
conn = st.connection("gsheets", type=GSheetsConnection)

# Helper function to get the current data
def get_data():
    return conn.read(ttl="0") # ttl="0" means it always gets the freshest data

# --- CALENDAR NAVIGATION ---
selected_date = st.date_input("Viewing To-Do List for:", datetime.today())
date_str = selected_date.strftime('%Y-%m-%d')

# Load the data from the Google Sheet
df = get_data()

st.divider()

# --- DISPLAY TASKS ---
st.subheader(f"📌 Missions for {selected_date.strftime('%B %d, %Y')}")

# Filter the spreadsheet for ONLY tasks matching the selected date
todays_tasks = df[df['date'] == date_str]

if todays_tasks.empty:
    st.info("No tasks for today. Chill vibes only. 🍃")
else:
    for index, row in todays_tasks.iterrows():
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            # Checkbox reflects the 'done' column in the sheet
            is_done = st.checkbox(row['task'], value=row['done'], key=f"task_{index}")
            
            # If the status changes, we update the sheet
            if is_done != row['done']:
                df.at[index, 'done'] = is_done
                conn.update(data=df)
                st.rerun()
        with col2:
            if st.button("❌", key=f"del_{index}"):
                df = df.drop(index)
                conn.update(data=df)
                st.rerun()

# --- ADD NEW TASK ---
with st.form(key="new_task_form", clear_on_submit=True):
    new_task = st.text_input("Add a new task...")
    if st.form_submit_button("Add Task ➕") and new_task:
        # Create a new row of data
        new_row = pd.DataFrame([{"date": date_str, "task": new_task, "done": False}])
        # Combine old data with new row and save to Google Sheets
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(data=updated_df)
        st.rerun()
