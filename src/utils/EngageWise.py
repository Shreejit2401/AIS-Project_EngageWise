import cv2
import time
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.FaceDetectionModule import FaceDetector
import dlib
from scipy.spatial import distance
from imutils import face_utils
from collections import OrderedDict
from fpdf import FPDF
import pygame

# Initialize constants
detector = FaceMeshDetector()
detector2 = FaceDetector()
EAR_THRESHOLD = 0.21
MAR_THRESHOLD = 0.6
ALARM_DURATION = 10
blink_count = 0
yawn_count = 0
awake_time = 0
drowsy_time = 0
distances = []
alarm_active = False
drowsy_start_time = None

# Initialize dlib and pygame
hog_face_detector = dlib.get_frontal_face_detector()
dlib_facelandmark = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
pygame.mixer.init()
alarm = pygame.mixer.Sound("alarm.mp3")

# Define landmark indices for eyes and mouth
FACIAL_LANDMARKS_IDXS = OrderedDict([
    ("mouth", (48, 68)),
    ("right_eyebrow", (17, 22)),
    ("left_eyebrow", (22, 27)),
    ("right_eye", (36, 42)),
    ("left_eye", (42, 48)),
    ("nose", (27, 35)),
    ("jaw", (0, 17))
])
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

# Helper functions
def calculate_EAR(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def calculate_MAR(mouth):
    return distance.euclidean(mouth[3], mouth[9]) / distance.euclidean(mouth[0], mouth[6])

def run_engagewise_session():
    global blink_count, yawn_count, awake_time, drowsy_time, alarm_active, drowsy_start_time

    cam = cv2.VideoCapture(0)
    cam.set(3, 3000)  # Set resolution width
    cam.set(4, 1700)   # Set resolution height

    while True:
        start_time = time.time()  # Start time for latency measurement

        ret, frame = cam.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Flip the frame horizontally
        frame, faces = detector.findFaceMesh(frame, draw=False)
        frame, bboxs = detector2.findFaces(frame, draw=False)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face = None

        for bbox in bboxs:
            x, y, w, h = bbox["bbox"]
            l, r = (x, y), (x + w, y + h)
            w = distance.euclidean(l, r)
            W, f = 6.3, 825
            d = (W * f) / w * 2.54
            distances.append(d)
            try:
                cv2.putText(frame, "Distance: {}cm".format(int(d)), (10, 90), cv2.FONT_HERSHEY_TRIPLEX, 0.7, (0, 0, 0), 2)
            except Exception as error:
                print(error)
                
        faces = hog_face_detector(gray)
        EAR = 0

        for face in faces:
            face_landmarks = dlib_facelandmark(gray, face)
            face_landmarks = face_utils.shape_to_np(face_landmarks)

            left_eye = face_landmarks[36:42]
            right_eye = face_landmarks[42:48]
            mouth = face_landmarks[mStart:mEnd]

            EAR = (calculate_EAR(left_eye) + calculate_EAR(right_eye)) / 2.0
            MAR = calculate_MAR(mouth)

            # Blink detection
            if EAR < EAR_THRESHOLD:
                blink_count += 1
                cv2.putText(frame, "Blink Detected!", (1100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

            # Yawn detection
            if MAR > MAR_THRESHOLD:
                yawn_count += 1
                cv2.putText(frame, "Yawn Detected!", (1100, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Drowsiness monitoring
        if EAR < EAR_THRESHOLD:
            if drowsy_start_time is None:
                drowsy_start_time = time.time()
            drowsy_time += 1

            if not alarm_active and time.time() - drowsy_start_time >= ALARM_DURATION:
                pygame.mixer.Sound.play(alarm)
                alarm_active = True
        else:
            drowsy_start_time = None
            alarm_active = False
            awake_time += 1

        # Calculate and display frame latency
        latency_ms = (time.time() - start_time) * 1000
        cv2.putText(frame, f"Latency: {latency_ms:.2f} ms", (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # Overlay statistics on the frame
        cv2.putText(frame, "Blink count: {}".format(blink_count), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, "Yawn count: {}".format(yawn_count), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, f"State: {'Drowsy' if EAR < EAR_THRESHOLD else 'Awake'}", (500, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

        yield frame

    cam.release()

def generate_pdf_report(pdf_name):
    global blink_count, yawn_count, awake_time, drowsy_time

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="EngageWise Session Report", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Blink Count: {blink_count}", ln=True)
    pdf.cell(200, 10, txt=f"Yawn Count: {yawn_count}", ln=True)
    pdf.cell(200, 10, txt=f"Time Awake: {awake_time} secs", ln=True)
    pdf.cell(200, 10, txt=f"Time Drowsy: {drowsy_time} secs", ln=True)
    pdf.output(pdf_name)