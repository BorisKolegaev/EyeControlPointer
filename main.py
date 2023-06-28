import cv2
import mediapipe as mp
import pyautogui
import numpy as np

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
smooth = 2
screen_width, screen_height = pyautogui.size()

plocX, plocY = 0, 0



while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    frame_height, frame_width, _ = frame.shape
    cv2.rectangle(frame, ((frame_width // 2) - 50, (frame_height // 2) - 20),
                  ((frame_width // 2) + 50, (frame_height // 2) + 20), (255, 0, 255), 2)

    if landmark_points:
        landmarks = landmark_points[0].landmark
        nose_bridge = landmarks[168]
        x = int(nose_bridge.x * frame_width)
        y = int(nose_bridge.y * frame_height)
        print(f'x {x} - y {y}')

        if ((frame_width // 2) - 50 < x < (frame_width // 2) + 50) and (
                (frame_height // 2) - 20 < y < (frame_height // 2) + 20):
            cv2.circle(frame, (x, y), 3, (0, 255, 0))
            x3 = np.interp(x, ((frame_width // 2) - 50, (frame_width // 2) + 50), (1, screen_width))
            y3 = np.interp(y, ((frame_height // 2) - 20, (frame_height // 2) + 20), (1, screen_height))
            clocX = plocX + (x3 - plocX) / smooth
            clocY = plocY + (y3 - plocY) / smooth
            pyautogui.moveTo(clocX, clocY)
            plocX, plocY = clocX, clocY

    cv2.imshow("res", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()