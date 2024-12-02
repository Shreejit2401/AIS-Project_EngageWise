import streamlit as st
import time
import numpy as np
from EngageWise import run_engagewise_session, generate_pdf_report
from EngageWise import blink_count, yawn_count, awake_time, drowsy_time, average_distance, average_latency
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt

# Constants
AUTH_PASSWORD = "3ngag3Wi$e"
VIDEO_FEED_KEY = "video_feed"
FEEDBACK_FILE = "monitoring/user_feedback.csv"
SESSIONS_FILE = "monitoring/sessions.csv"

# Initialize session state variables
if "SESSION_RUNNING" not in st.session_state:
    st.session_state["SESSION_RUNNING"] = False
if "FEEDBACK_SUBMITTED" not in st.session_state:
    st.session_state["FEEDBACK_SUBMITTED"] = False
if "SHOW_FEEDBACK_FORM" not in st.session_state:
    st.session_state["SHOW_FEEDBACK_FORM"] = False
if "SHOW_VISUALIZATION" not in st.session_state:
    st.session_state["SHOW_VISUALIZATION"] = False

# Initialize session metrics CSV if it doesn't exist
if not os.path.exists(SESSIONS_FILE):
    with open(SESSIONS_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "User ID", "Session Time", "Blink Count", "Yawn Count", "Awake Time",
                         "Drowsy Time", "Average Distance (cm)", "Average Latency (ms)"])

# Streamlit app UI
st.title("Welcome to EngageWise!!")
st.sidebar.header("User Authentication")

# Authentication
username = st.sidebar.text_input("Enter your name")
user_id = st.sidebar.text_input("Enter your unique ID")

# Consent checkbox
consent_given = st.sidebar.checkbox(
    "**I consent to allow 'EngageWise' to capture my facial landmarks for seamless functionality. "
    "Note: we do not store any facial features or images captured during the session.**"
)

# Conditional password input based on consent
if consent_given:
    password = st.sidebar.text_input("Password", type="password")
else:
    password = ""
    st.sidebar.warning("Please provide consent to enter your password.")

st.sidebar.subheader("Alarm Settings")
ALARM_DURATION = st.sidebar.slider("Drowsiness Threshold (seconds)", 1, 60, 10)
alarm_file_path = st.sidebar.file_uploader("Upload Sound file", type=["mp3", "wav"])

if alarm_file_path:
    with open("src/utils/alarm_temp.mp3", "wb") as f:
        f.write(alarm_file_path.read())
    alarm_file_path = "src/utils/alarm_temp.mp3"

# Initialize the feedback CSV file if it doesn't exist
if not os.path.exists(FEEDBACK_FILE):
    with open(FEEDBACK_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "User ID", "Feedback", "Comments"])

# Session management
if st.sidebar.button("Start Session"):
    if password == AUTH_PASSWORD:
        st.session_state["SESSION_RUNNING"] = True
        st.session_state["FEEDBACK_SUBMITTED"] = False
        st.session_state["SHOW_FEEDBACK_FORM"] = False
        st.session_state["session_start_time"] = time.time()  # Store start time
        st.success(f"Session started for {username} (ID: {user_id})")
        st.session_state[VIDEO_FEED_KEY] = st.empty()

        for frame in run_engagewise_session(ALARM_DURATION, alarm_file_path):
            st.session_state[VIDEO_FEED_KEY].image(frame, channels="BGR", use_container_width=True)
    else:
        st.error("Unauthorized access. Please check your password.")

if st.sidebar.button("Stop Session"):
    if st.session_state["SESSION_RUNNING"]:
        st.session_state["SESSION_RUNNING"] = False
        st.session_state[VIDEO_FEED_KEY].empty()
        st.success("Session stopped. Generating report...")

        session_end_time = time.time()
        session_time = round(session_end_time - st.session_state["session_start_time"])  # Use session_state

        # Automatically generate PDF report with dynamic filename
        pdf_filename = f"{username}_{user_id}.pdf"
        generate_pdf_report(pdf_filename)
        st.success(f"Report saved as {pdf_filename}")

        # Collect and append session metrics
        with open(SESSIONS_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([username, user_id, session_time, blink_count, yawn_count,
                             awake_time, drowsy_time, average_distance, average_latency])

        st.session_state["SHOW_FEEDBACK_FORM"] = True  # Show the feedback form now

# Feedback form
if st.session_state["SHOW_FEEDBACK_FORM"]:
    st.header("Download Report and Provide Feedback")
    with open(f"{username}_{user_id}.pdf", "rb") as pdf:
        st.download_button("Download Report", data=pdf, file_name=f"{username}_{user_id}.pdf")

    if not st.session_state["FEEDBACK_SUBMITTED"]:
        st.header("User Feedback")
        like_dislike = st.radio("Did you find the app helpful?", ["Like", "Dislike"], key="feedback_radio")
        feedback_text = st.text_area("Additional feedback (optional)", key="feedback_text")

        if st.button("Submit Feedback"):
            if username and user_id:
                with open(FEEDBACK_FILE, mode="a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([username, user_id, like_dislike, feedback_text])
                st.success("Thank you for your feedback!")
                st.session_state["FEEDBACK_SUBMITTED"] = True
                st.session_state["SHOW_VISUALIZATION"] = True
            else:
                st.error("Please provide your name and ID before submitting feedback.")

# Visualization trigger
if st.session_state["SHOW_VISUALIZATION"]:
    st.header("Session Metrics Visualization")

    session_data = pd.read_csv(SESSIONS_FILE)

    metrics = {
        "Blink Count": (session_data["Blink Count"].iloc[-1], 20),
        "Yawn Count": (session_data["Yawn Count"].iloc[-1], 5),
        "Awake Time": (session_data["Awake Time"].iloc[-1], session_data["Session Time"].iloc[-1]),
        "Drowsy Time": (session_data["Drowsy Time"].iloc[-1], 0),
        "Average Distance (cm)": (session_data["Average Distance (cm)"].iloc[-1], 60),
        "Average Latency (ms)": (session_data["Average Latency (ms)"].iloc[-1], 100)
    }

    for metric, (value, ideal) in metrics.items():
        fig, ax = plt.subplots()
        ax.bar(["Current Session", "Ideal Value"], [value, ideal], color=['red', 'green'])
        plt.title(f"{metric} Comparison")
        plt.ylabel(metric)
        st.pyplot(fig)

    if st.button("Ready for next session"):
        st.session_state["SHOW_VISUALIZATION"] = False
        st.session_state["FEEDBACK_SUBMITTED"] = False
        st.write("Ready for the next session!")


































# import streamlit as st
# import time
# import numpy as np
# from EngageWise import run_engagewise_session, generate_pdf_report
# from EngageWise import blink_count, yawn_count, awake_time, drowsy_time, average_distance, average_latency
# import os
# import csv
# import pandas as pd
# import matplotlib.pyplot as plt

# # Constants
# AUTH_PASSWORD = "3ngag3Wi$e"
# VIDEO_FEED_KEY = "video_feed"
# FEEDBACK_FILE = "monitoring/user_feedback.csv"
# SESSIONS_FILE = "monitoring/sessions.csv"

# # Initialize session state variables
# if "SESSION_RUNNING" not in st.session_state:
#     st.session_state["SESSION_RUNNING"] = False
# if "FEEDBACK_SUBMITTED" not in st.session_state:
#     st.session_state["FEEDBACK_SUBMITTED"] = False
# if "SHOW_FEEDBACK_FORM" not in st.session_state:
#     st.session_state["SHOW_FEEDBACK_FORM"] = False
# if "SHOW_VISUALIZATION" not in st.session_state:
#     st.session_state["SHOW_VISUALIZATION"] = False

# # Initialize session metrics CSV if it doesn't exist
# if not os.path.exists(SESSIONS_FILE):
#     with open(SESSIONS_FILE, mode="w", newline="") as file:
#         writer = csv.writer(file)
#         writer.writerow(["Username", "User ID", "Session Time", "Blink Count", "Yawn Count", "Awake Time",
#                          "Drowsy Time", "Average Distance (cm)", "Average Latency (ms)"])

# # Streamlit app UI
# st.title("EngageWise Monitoring Application")
# st.sidebar.header("User Authentication")

# # Authentication
# username = st.sidebar.text_input("Enter your name")
# user_id = st.sidebar.text_input("Enter your unique ID")
# password = st.sidebar.text_input("Password", type="password")

# st.sidebar.subheader("Alarm Settings")
# ALARM_DURATION = st.sidebar.slider("Alarm Duration (seconds)", 1, 60, 10)
# alarm_file_path = st.sidebar.file_uploader("Upload Alarm Sound", type=["mp3", "wav"])

# if alarm_file_path:
#     with open("src/utils/alarm_temp.mp3", "wb") as f:
#         f.write(alarm_file_path.read())

# alarm_file_path = "src/utils/alarm_temp.mp3"

# # Initialize the feedback CSV file if it doesn't exist
# if not os.path.exists(FEEDBACK_FILE):
#     with open(FEEDBACK_FILE, mode="w", newline="") as file:
#         writer = csv.writer(file)
#         writer.writerow(["Username", "User ID", "Feedback", "Comments"])

# # Session management
# if st.sidebar.button("Start Session"):
#     if password == AUTH_PASSWORD:
#         st.session_state["SESSION_RUNNING"] = True
#         st.session_state["FEEDBACK_SUBMITTED"] = False
#         st.session_state["SHOW_FEEDBACK_FORM"] = False
#         st.session_state["session_start_time"] = time.time()  # Store start time
#         st.success(f"Session started for {username} (ID: {user_id})")
#         st.session_state[VIDEO_FEED_KEY] = st.empty()

#         for frame in run_engagewise_session(ALARM_DURATION, alarm_file_path):
#             st.session_state[VIDEO_FEED_KEY].image(frame, channels="BGR", use_container_width=True)
#     else:
#         st.error("Unauthorized access. Please check your password.")

# if st.sidebar.button("Stop Session"):
#     if st.session_state["SESSION_RUNNING"]:
#         st.session_state["SESSION_RUNNING"] = False
#         st.session_state[VIDEO_FEED_KEY].empty()
#         st.success("Session stopped. Generating report...")

#         session_end_time = time.time()
#         session_time = round(session_end_time - st.session_state["session_start_time"])  # Use session_state

#         # Automatically generate PDF report with dynamic filename
#         pdf_filename = f"{username}_{user_id}.pdf"
#         generate_pdf_report(pdf_filename)
#         st.success(f"Report saved as {pdf_filename}")

#         # Collect and append session metrics
#         with open(SESSIONS_FILE, mode="a", newline="") as file:
#             writer = csv.writer(file)
#             writer.writerow([username, user_id, session_time, blink_count, yawn_count,
#                              awake_time, drowsy_time, average_distance, average_latency])

#         st.session_state["SHOW_FEEDBACK_FORM"] = True  # Show the feedback form now

# # Feedback form
# if st.session_state["SHOW_FEEDBACK_FORM"]:
#     st.header("Download Report and Provide Feedback")
#     with open(f"{username}_{user_id}.pdf", "rb") as pdf:
#         st.download_button("Download Report", data=pdf, file_name=f"{username}_{user_id}.pdf")

#     if not st.session_state["FEEDBACK_SUBMITTED"]:
#         st.header("User Feedback")
#         like_dislike = st.radio("Did you find the app helpful?", ["Like", "Dislike"], key="feedback_radio")
#         feedback_text = st.text_area("Additional feedback (optional)", key="feedback_text")

#         if st.button("Submit Feedback"):
#             if username and user_id:
#                 with open(FEEDBACK_FILE, mode="a", newline="") as file:
#                     writer = csv.writer(file)
#                     writer.writerow([username, user_id, like_dislike, feedback_text])
#                 st.success("Thank you for your feedback!")
#                 st.session_state["FEEDBACK_SUBMITTED"] = True
#                 st.session_state["SHOW_VISUALIZATION"] = True
#             else:
#                 st.error("Please provide your name and ID before submitting feedback.")

# # Visualization trigger
# if st.session_state["SHOW_VISUALIZATION"]:
#     st.header("Session Metrics Visualization")

#     session_data = pd.read_csv(SESSIONS_FILE)

#     metrics = {
#         "Blink Count": (session_data["Blink Count"].iloc[-1], 20),
#         "Yawn Count": (session_data["Yawn Count"].iloc[-1], 5),
#         "Awake Time": (session_data["Awake Time"].iloc[-1], session_data["Session Time"].iloc[-1]),
#         "Drowsy Time": (session_data["Drowsy Time"].iloc[-1], 0),
#         "Average Distance (cm)": (session_data["Average Distance (cm)"].iloc[-1], 60),
#         "Average Latency (ms)": (session_data["Average Latency (ms)"].iloc[-1], 100)
#     }

#     for metric, (value, ideal) in metrics.items():
#         fig, ax = plt.subplots()
#         ax.bar(["Current Session", "Ideal Value"], [value, ideal], color=['red', 'green'])
#         plt.title(f"{metric} Comparison")
#         plt.ylabel(metric)
#         st.pyplot(fig)

#     if st.button("Ready for next session"):
#         st.session_state["SHOW_VISUALIZATION"] = False
#         st.session_state["FEEDBACK_SUBMITTED"] = False
#         st.write("Ready for the next session!")

# # # Optional manual navigation
# # if st.sidebar.button("View Session Visualizations"):
# #     st.session_state["SHOW_VISUALIZATION"] = True