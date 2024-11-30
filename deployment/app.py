import streamlit as st
import cv2
import numpy as np
from EngageWise import run_engagewise_session, generate_pdf_report

# Constants
AUTH_PASSWORD = "3ngag3Wi$e"
SESSION_RUNNING = False
VIDEO_FEED_KEY = "video_feed"

# Streamlit app UI
st.title("EngageWise Monitoring Application")
st.sidebar.header("User Authentication")

# Authentication
username = st.sidebar.text_input("Enter your name")
user_id = st.sidebar.text_input("Enter your unique ID")
password = st.sidebar.text_input("Password", type="password")

# Session management
if st.sidebar.button("Start Session"):
    if password == AUTH_PASSWORD:
        st.session_state["SESSION_RUNNING"] = True
        st.success(f"Session started for {username} (ID: {user_id})")

        # Start the live video feed in the main window
        st.session_state[VIDEO_FEED_KEY] = st.empty()
        for frame in run_engagewise_session():
            st.session_state[VIDEO_FEED_KEY].image(frame, channels="BGR", use_container_width=True)
    else:
        st.error("Unauthorized access. Please check your password.")

if st.sidebar.button("Stop Session"):
    if st.session_state.get("SESSION_RUNNING"):
        st.session_state["SESSION_RUNNING"] = False
        st.session_state[VIDEO_FEED_KEY].empty()
        st.success("Session stopped. Generating report...")

        # Ask for the PDF name
        pdf_name = st.text_input("Enter the PDF file name (without extension)")
        if pdf_name:
            pdf_path = f"{pdf_name}.pdf"
            generate_pdf_report(pdf_path)
            st.success(f"Report saved as {pdf_path}")
            with open(pdf_path, "rb") as pdf:
                st.download_button("Download Report", data=pdf, file_name=pdf_path)
            
        # Feedback section
        st.header("User Feedback")
        like_dislike = st.radio("Did you find the app helpful?", ["Like", "Dislike"])
        feedback_text = st.text_area("Additional feedback (optional)")
        if st.button("Submit Feedback"):
            if username and user_id:
                with open("user_feedback.txt", "a") as f:
                    f.write(f"User: {username}, ID: {user_id}, Feedback: {like_dislike}\n")
                    f.write(f"Comments: {feedback_text}\n\n")
                st.success("Thank you for your feedback!")
            else:
                st.error("Please provide your name and ID before submitting feedback.")
    else:
        st.warning("No session is running.")