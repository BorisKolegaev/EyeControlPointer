import cv2
import mediapipe as mp
import pyautogui
import numpy as np

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

plocX, plocY = 0, 0
clocX, clocY = 0, 0

smooth = 2

frameR = 200
screen_w, screen_h = pyautogui.size()
wCam, hCam = 640, 480

while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape
    cv2.rectangle(frame, (frameR, frameR), (frame_w - frameR, frame_h - frameR), (255, 0, 255), 2)
    if landmark_points:
        landmarks = landmark_points[0].landmark

        landmark = landmarks[475]
        left_eye = landmarks[475]
        x = int(landmark.x * frame_w)
        y = int(landmark.y * frame_h)
        #print(f'x {x} - y {y}')

        if (frameR < x < (frame_w - frameR)) and (frameR < y < (frame_h - frameR)):
            cv2.circle(frame, (x, y), 3, (0, 255, 0))

            x3 = np.interp(x, (frameR, frame_w - frameR), (1, screen_w))
            y3 = np.interp(y, (frameR, frame_h - frameR), (1, screen_h))
            print(f'x {x3} - y {y3}')

            clocX = plocX + (x3 - plocX) / smooth
            clocY = plocY + (y3 - plocY) / smooth

            pyautogui.moveTo(clocX, clocY)

            plocX, plocY = clocX, clocY

    cv2.imshow('Eye Controlled Mouse', frame)
    cv2.waitKey(1)