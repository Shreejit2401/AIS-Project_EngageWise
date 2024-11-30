import cv2
from scipy.spatial import distance
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.FaceDetectionModule import FaceDetector
from imutils import face_utils
import numpy as np
import dlib
from collections import OrderedDict
import pygame
import time
import getpass

AUTH_PASSWORD = "3ngag3Wi$e"

def authenticate_user():
    password = getpass.getpass("Enter password to start EngageWise: ")
    if password != AUTH_PASSWORD:
        print("Unauthorized access. Exiting program.")
        exit()

authenticate_user()

def calculate_EAR(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear_aspect_ratio = (A + B) / (2.0 * C)
    return ear_aspect_ratio

def cal_MAR(mouth):
    dist_x = distance.euclidean(mouth[0], mouth[6])
    dist_y = distance.euclidean(mouth[3], mouth[9])
    mar = dist_y / dist_x
    return mar

FACIAL_LANDMARKS_IDXS = OrderedDict([
    ("mouth", (48, 68)),
    ("right_eyebrow", (17, 22)),
    ("left_eyebrow", (22, 27)),
    ("right_eye", (36, 42)),
    ("left_eye", (42, 48)),
    ("nose", (27, 35)),
    ("jaw", (0, 17))
])

cam = cv2.VideoCapture(0)
cam.set(3, 3000)
cam.set(4, 1700)

hog_face_detector = dlib.get_frontal_face_detector()
dlib_facelandmark = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

detector = FaceMeshDetector()
detector2 = FaceDetector()
blink_flag = False
yawn_flag = False
EAR_THRESHOLD = 0.21
MAR_THRESHOLD = 0.6
ALARM_DURATION = 10
blink_count = 0
yawn_count = 0
state = ""

pygame.mixer.init()
alarm = pygame.mixer.Sound("alarm.mp3")
number = 0

while True:
    try:
        ret, frame = cam.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting....")
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.GaussianBlur(frame, (7, 7), 0)

        frame, faces = detector.findFaceMesh(frame, draw=False)
        frame, bboxs = detector2.findFaces(frame, draw=False)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for bbox in bboxs:
            x, y, w, h = bbox["bbox"]
            l, r = (x, y), (x + w, y + h)
            w = distance.euclidean(l, r)
            W, f = 6.3, 825
            d = (W * f) / w * 2.54
            cv2.putText(frame, "Distance: {}cm".format(int(d)), (10, 90), cv2.FONT_HERSHEY_TRIPLEX, 0.7, (0, 0, 0), 2)

        faces = hog_face_detector(gray)
        EAR = 0

        for face in faces:
            face_landmarks = dlib_facelandmark(gray, face)
            face_landmarks = face_utils.shape_to_np(face_landmarks)
            leftEye = face_landmarks[36:42]
            rightEye = face_landmarks[42:48]
            mouth = face_landmarks[mStart:mEnd]

            left_ear = calculate_EAR(leftEye)
            right_ear = calculate_EAR(rightEye)
            mar = cal_MAR(mouth)
            EAR = (left_ear + right_ear) / 2

            if EAR < EAR_THRESHOLD:
                if not blink_flag:
                    blink_flag = True
                    blink_count += 1
                    cv2.putText(frame, "Blink Detected!", (1100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            else:
                blink_flag = False

            if mar > MAR_THRESHOLD:
                if not yawn_flag:
                    yawn_flag = True
                    yawn_count += 1
                    cv2.putText(frame, "Yawn Detected!", (1100, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            else:
                yawn_flag = False

        cv2.putText(frame, "Blink count: {}".format(blink_count), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, "Yawn count: {}".format(yawn_count), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        if EAR < EAR_THRESHOLD:
            if state != "Drowsy":
                drowsy_start_time = time.time()
                alarm_active = False
            state = "Drowsy"
            
            if not alarm_active and time.time() - drowsy_start_time >= ALARM_DURATION:
                pygame.mixer.Sound.play(alarm)
                alarm_active = True
        else:
            state = "Awake"
            drowsy_start_time = None
        
        cv2.putText(frame, f"{state}", (500, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

        key = cv2.waitKey(1)
        if key == ord('c'):
            number += 1
            print(f"Image {number} has been captured")
            cv2.imwrite(f'image{number}.png', frame.copy())
        if key == ord('q'):
            cv2.destroyAllWindows()
            break

        cv2.imshow("Image", frame)

    except Exception as e:
        print(f"An error occurred: {e}")
        break

cam.release()
cv2.destroyAllWindows()