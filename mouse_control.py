import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QPainter

import mediapipe as mp
import pyautogui
import numpy as np

class TransparentRectangle(QWidget):
    def __init__(self, left, top, width, height, border_width):
        super().__init__()

        # Set the window attributes for transparency and no click-through
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setWindowOpacity(0.1)  # Set the window opacity to 0.5 for semi-transparency

        # Analyze screen resolution
        screen_rect = QDesktopWidget().screenGeometry()
        screen_width, screen_height = screen_rect.width(), screen_rect.height()

        # Calculate the position to center the rectangle on the screen
        rect_left = (screen_width - width) // 2
        rect_top = ((screen_height - height) // 2) - 100

        # Set the size and position of the rectangle
        self.setGeometry(rect_left, rect_top, width, height)

        # Store the border width
        self.border_width = border_width

        # Create a QLabel widget to display the video frame
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, width, height)
        self.label.setAlignment(Qt.AlignCenter)

        # Create a timer to periodically update the frame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update frame every 30 milliseconds

        # Initialize variables for face tracking
        self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.smooth = 2
        self.screen_width, self.screen_height = pyautogui.size()
        self.plocX, self.plocY = 0, 0
        

    ##TO_DO
    def opacity_status(self, status=False):
        if status:
            status = False
            self.setWindowOpacity(0.1)
            return
        status = True

    def update_frame(self):
        # Read a frame from the webcam
        ret, frame = self.cam.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)

        # Perform face tracking
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = self.face_mesh.process(rgb_frame)
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
                x3 = np.interp(x, ((frame_width // 2) - 50, (frame_width // 2) + 50), (1, self.screen_width))
                y3 = np.interp(y, ((frame_height // 2) - 20, (frame_height // 2) + 20), (1, self.screen_height))
                clocX = self.plocX + (x3 - self.plocX) / self.smooth
                clocY = self.plocY + (y3 - self.plocY) / self.smooth
                pyautogui.moveTo(clocX, clocY)
                self.plocX, self.plocY = clocX, clocY

                # Crop the region within the rectangle
                rect_left = (frame_width // 2) - 50
                rect_top = (frame_height // 2) - 20
                rect_right = (frame_width // 2) + 50
                rect_bottom = (frame_height // 2) + 20
                cropped_frame = frame[rect_top:rect_bottom, rect_left:rect_right]

                # Convert the cropped frame to RGB format for display in QLabel
                cropped_frame_rgb = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)

                # Convert the cropped frame to QImage format
                cropped_height, cropped_width, _ = cropped_frame_rgb.shape
                cropped_q_image = QImage(cropped_frame_rgb.data, cropped_width, cropped_height, QImage.Format_RGB888)

                # Convert the QImage to QPixmap for display
                cropped_pixmap = QPixmap.fromImage(cropped_q_image)

                # Set the cropped pixmap on the QLabel
                self.label.setPixmap(cropped_pixmap)

                return

        # Convert the frame to RGB format for display in QLabel
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the frame to QImage format
        height, width, channel = frame_rgb.shape
        q_image = QImage(frame_rgb.data, width, height, QImage.Format_RGB888)

        # Convert the QImage to QPixmap for display
        pixmap = QPixmap.fromImage(q_image)

        # Set the pixmap on the QLabel
        self.label.setPixmap(pixmap)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = painter.pen()
        pen.setColor(Qt.red)
        pen.setWidth(self.border_width)
        painter.setPen(pen)

        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Example usage: create a transparent rectangle with red border
    rectangle = TransparentRectangle(0, 0, 500, 300, 2)
    rectangle.show()

    sys.exit(app.exec_())