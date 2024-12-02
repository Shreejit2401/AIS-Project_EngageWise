import cv2
import time
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.FaceDetectionModule import FaceDetector
import dlib
from scipy.spatial import distance
from imutils import face_utils
from collections import OrderedDict
from fpdf import FPDF
import os
import pygame

# Initialize constants
detector = FaceMeshDetector()
detector2 = FaceDetector()
EAR_THRESHOLD = 0.21
MAR_THRESHOLD = 0.6
blink_count = 0
yawn_count = 0
awake_time = 0
drowsy_time = 0
distances = []
latency = []
latency_ms = 0
alarm_active = False
drowsy_start_time = None
blink_flag = False
yawn_flag = False
average_distance = 0
average_latency = 0
ALARM_DURATION = 10
alarm_file_path = ("src/utils/alarm_temp.mp3" if os.path.exists("src/utils/alarm_temp.mp3") else "src/utils/alarm.mp3")

# Initialize dlib and pygame
hog_face_detector = dlib.get_frontal_face_detector()
dlib_facelandmark = dlib.shape_predictor("src/utils/shape_predictor_68_face_landmarks.dat")
pygame.mixer.init()

# Helper functions
def play_alarm():
    pygame.mixer.Sound(alarm_file_path).play()

def calculate_EAR(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def calculate_MAR(mouth):
    return distance.euclidean(mouth[3], mouth[9]) / distance.euclidean(mouth[0], mouth[6])

def run_engagewise_session(ALARM_DURATION, alarm_file_path):
    global blink_count, yawn_count, awake_time, drowsy_time, alarm_active, drowsy_start_time, latency_ms, blink_flag, yawn_flag

    cam = cv2.VideoCapture(0)
    cam.set(3, 3000)
    cam.set(4, 1700)

    while True:
        start_time = time.time()
        ret, frame = cam.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        _, bboxs = detector2.findFaces(frame, draw=False)
        for bbox in bboxs:
            x, y, w, h = bbox["bbox"]
            W, f = 6.3, 825
            face_width = distance.euclidean((x, y), (x + w, y + h))
            distance_cm = (W * f) / face_width * 2.54
            distances.append(distance_cm)

        faces = hog_face_detector(gray)
        EAR = 0
        
        for face in faces:
            shape = dlib_facelandmark(gray, face)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[36:42]
            rightEye = shape[42:48]
            mouth = shape[48:68]
            EAR = (calculate_EAR(leftEye) + calculate_EAR(rightEye)) / 2
            MAR = calculate_MAR(mouth)

            if EAR < EAR_THRESHOLD:
                if not blink_flag:
                    blink_flag = True
                    blink_count += 1
                    cv2.putText(frame, "Blink Detected!", (1100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            else:
                blink_flag = False

            if MAR > MAR_THRESHOLD:
                if not yawn_flag:
                    yawn_flag = True
                    yawn_count += 1
                    cv2.putText(frame, "Yawn Detected!", (1100, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            else:
                yawn_flag = False

        if EAR < EAR_THRESHOLD:
            if drowsy_start_time is None:
                drowsy_start_time = time.time()
            drowsy_time += 1

            if not alarm_active and time.time() - drowsy_start_time >= ALARM_DURATION:
                play_alarm()
                alarm_active = True
                
        else:
            drowsy_start_time = None
            alarm_active = False
            awake_time += 1

        latency_ms = (time.time() - start_time) * 1000
        latency.append(latency_ms)
        cv2.putText(frame, f"Latency: {latency_ms:.2f} ms", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        cv2.putText(frame, f"Blink Count: {blink_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, f"Yawn Count: {yawn_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, f"State: {'Drowsy' if EAR < EAR_THRESHOLD else 'Awake'}", (500, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

        yield frame

    cam.release()

def generate_pdf_report(pdf_name):
    global blink_count, yawn_count, awake_time, drowsy_time, average_distance, distances, latency_ms, latency, average_distance, average_latency
    
    average_distance = sum(distances) / len(distances) if distances else 0
    average_latency = sum(latency) / len(latency) if latency else 0

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="EngageWise Session Report", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Blink Count: {blink_count}", ln=True)
    pdf.cell(200, 10, txt=f"Yawn Count: {yawn_count}", ln=True)
    pdf.cell(200, 10, txt=f"Time Awake: {awake_time} secs", ln=True)
    pdf.cell(200, 10, txt=f"Time Drowsy: {drowsy_time} secs", ln=True)
    pdf.cell(200, 10, txt=f"Average distance: {average_distance:.2f} cm", ln=True)
    pdf.cell(200, 10, txt=f"Average latency: {average_latency:.2f} cm", ln=True)
    pdf.output(pdf_name)





















# import cv2
# import time
# from cvzone.FaceMeshModule import FaceMeshDetector
# from cvzone.FaceDetectionModule import FaceDetector
# import dlib
# from scipy.spatial import distance
# from imutils import face_utils
# from collections import OrderedDict
# from fpdf import FPDF
# import pygame

# # Initialize constants
# detector = FaceMeshDetector()
# detector2 = FaceDetector()
# EAR_THRESHOLD = 0.21
# MAR_THRESHOLD = 0.6
# ALARM_DURATION = 10
# blink_count = 0
# yawn_count = 0
# awake_time = 0
# drowsy_time = 0
# distances = []
# latency = []
# latency_ms = 0
# alarm_active = False
# drowsy_start_time = None
# blink_flag = False
# yawn_flag = False
# average_distance = 0
# average_latency = 0

# # Initialize dlib and pygame
# hog_face_detector = dlib.get_frontal_face_detector()
# dlib_facelandmark = dlib.shape_predictor("src/shape_predictor_68_face_landmarks.dat")
# pygame.mixer.init()
# alarm = pygame.mixer.Sound("src/alarm.mp3")

# # Define landmark indices for eyes and mouth
# FACIAL_LANDMARKS_IDXS = OrderedDict([
#     ("mouth", (48, 68)),
#     ("right_eye", (36, 42)),
#     ("left_eye", (42, 48))
# ])
# (mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

# # Helper functions
# def calculate_EAR(eye):
#     A = distance.euclidean(eye[1], eye[5])
#     B = distance.euclidean(eye[2], eye[4])
#     C = distance.euclidean(eye[0], eye[3])
#     return (A + B) / (2.0 * C)

# def calculate_MAR(mouth):
#     return distance.euclidean(mouth[3], mouth[9]) / distance.euclidean(mouth[0], mouth[6])

# def run_engagewise_session():
#     global blink_count, yawn_count, awake_time, drowsy_time, alarm_active, drowsy_start_time, latency_ms, blink_flag, yawn_flag

#     cam = cv2.VideoCapture(0)
#     cam.set(3, 3000)  # Set resolution width
#     cam.set(4, 1700)   # Set resolution height

#     while True:
#         start_time = time.time()  # Start time for latency measurement

#         ret, frame = cam.read()
#         if not ret:
#             break

#         frame = cv2.flip(frame, 1)
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
#         _, bboxs = detector2.findFaces(frame, draw=False)
#         for bbox in bboxs:
#             x, y, w, h = bbox["bbox"]
#             W, f = 6.3, 825
#             face_width = distance.euclidean((x, y), (x + w, y + h))
#             distance_cm = (W * f) / face_width * 2.54
#             distances.append(distance_cm)

#         faces = hog_face_detector(gray)
#         EAR=0
        
#         for face in faces:
#             shape = dlib_facelandmark(gray, face)
#             shape = face_utils.shape_to_np(shape)

#             leftEye = shape[36:42]
#             rightEye = shape[42:48]
#             mouth = shape[48:68]
#             EAR = (calculate_EAR(leftEye) + calculate_EAR(rightEye)) / 2
#             MAR = calculate_MAR(mouth)

#             if EAR < EAR_THRESHOLD:
#                 if not blink_flag:
#                     blink_flag = True
#                     blink_count += 1
#                     cv2.putText(frame, "Blink Detected!", (1100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
#             else:
#                 blink_flag = False

#             if MAR > MAR_THRESHOLD:
#                 if not yawn_flag:
#                     yawn_flag = True
#                     yawn_count += 1
#                     cv2.putText(frame, "Yawn Detected!", (1100, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
#             else:
#                 yawn_flag = False

#         # Drowsiness monitoring
#         if EAR < EAR_THRESHOLD:
#             if drowsy_start_time is None:
#                 drowsy_start_time = time.time()
#             drowsy_time += 1

#             if not alarm_active and time.time() - drowsy_start_time >= ALARM_DURATION:
#                 pygame.mixer.Sound.play(alarm)
#                 alarm_active = True
#         else:
#             drowsy_start_time = None
#             alarm_active = False
#             awake_time += 1

#         # Calculate and display frame latency
#         latency_ms = (time.time() - start_time) * 1000
#         latency.append(latency_ms)
#         cv2.putText(frame, f"Latency: {latency_ms:.2f} ms", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

#         # Overlay statistics on the frame
#         cv2.putText(frame, f"Blink Count: {blink_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
#         cv2.putText(frame, f"Yawn Count: {yawn_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
#         cv2.putText(frame, f"State: {'Drowsy' if EAR < EAR_THRESHOLD else 'Awake'}", (500, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

#         yield frame

#     cam.release()


# def generate_pdf_report(pdf_name):
#     global blink_count, yawn_count, awake_time, drowsy_time, average_distance, distances, latency_ms, latency, average_distance, average_latency
    
#     average_distance = sum(distances) / len(distances) if distances else 0
#     average_latency = sum(latency) / len(latency) if latency else 0

#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#     pdf.cell(200, 10, txt="EngageWise Session Report", ln=True, align='C')
#     pdf.cell(200, 10, txt=f"Blink Count: {blink_count}", ln=True)
#     pdf.cell(200, 10, txt=f"Yawn Count: {yawn_count}", ln=True)
#     pdf.cell(200, 10, txt=f"Time Awake: {awake_time} secs", ln=True)
#     pdf.cell(200, 10, txt=f"Time Drowsy: {drowsy_time} secs", ln=True)
#     pdf.cell(200, 10, txt=f"Average distance: {average_distance:.2f} cm", ln=True)
#     pdf.cell(200, 10, txt=f"Average latency: {average_latency:.2f} cm", ln=True)
#     pdf.output(pdf_name)