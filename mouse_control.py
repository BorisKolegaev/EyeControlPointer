import sys
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QPainter


class TransparentRectangle(QWidget):
    def __init__(self, left, top, width, height, border_width):
        super().__init__()

        # Устанавливаем атрибуты окна для прозрачности и невозможности щелчка
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setWindowOpacity(0.1)  # Устанавливаем прозрачность окна на 0.1 для полупрозрачности
        self.eyes_in_area = False

        # Анализируем разрешение экрана
        screen_rect = QDesktopWidget().screenGeometry()
        screen_width, screen_height = screen_rect.width(), screen_rect.height()

        # Рассчитываем положение для центрирования прямоугольника на экране
        rect_left = (screen_width - width) // 2
        rect_top = ((screen_height - height) // 2) - 100

        # Устанавливаем размер и положение прямоугольника
        self.setGeometry(rect_left, rect_top, width, height)

        # Храним ширину границы
        self.border_width = border_width

        # Создаем виджет QLabel для отображения видеокадра
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, width, height)
        self.label.setAlignment(Qt.AlignCenter)

        # Создаем таймер для периодического обновления кадра
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Обновляем кадр каждые 30 миллисекунд

        # Инициализируем переменные для отслеживания лица
        self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.smooth = 2
        self.screen_width, self.screen_height = pyautogui.size()
        self.plocX, self.plocY = 0, 0

    def opacity_status(self, status=False):
        if self.eyes_in_area == status:
            return
        elif status:
            self.eyes_in_area = True
            self.setWindowOpacity(0.5)
            return
        else:
            self.eyes_in_area = False
            self.setWindowOpacity(0.1)
            return

    def update_frame(self):
        # Считываем кадр с веб-камеры
        ret, frame = self.cam.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)

        # Выполняем отслеживание лица
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = self.face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks
        frame_height, frame_width, _ = frame.shape
        cv2.rectangle(frame, ((frame_width // 2) - 50, (frame_height // 2) - 20),
                      ((frame_width // 2) + 50, (frame_height // 2) + 20), (255, 255, 255), 2)

        if landmark_points:
            landmarks = landmark_points[0].landmark
            nose_bridge = landmarks[168]
            x = int(nose_bridge.x * frame_width)
            y = int(nose_bridge.y * frame_height)
            print(f'x {x} - y {y}')

            if ((frame_width // 2) - 50 < x < (frame_width // 2) + 50) and (
                    (frame_height // 2) - 20 < y < (frame_height // 2) + 20):
                self.opacity_status(True)
                cv2.circle(frame, (x, y), 3, (0, 255, 0))
                x3 = np.interp(x, ((frame_width // 2) - 50, (frame_width // 2) + 50), (1, self.screen_width))
                y3 = np.interp(y, ((frame_height // 2) - 20, (frame_height // 2) + 20), (1, self.screen_height))
                clocX = self.plocX + (x3 - self.plocX) / self.smooth
                clocY = self.plocY + (y3 - self.plocY) / self.smooth
                pyautogui.moveTo(clocX, clocY)
                self.plocX, self.plocY = clocX, clocY

                # Обрезаем область внутри прямоугольника
                rect_left = (frame_width // 2) - 50
                rect_top = (frame_height // 2) - 20
                rect_right = (frame_width // 2) + 50
                rect_bottom = (frame_height // 2) + 20
                cropped_frame = frame[rect_top:rect_bottom, rect_left:rect_right]

                # Преобразуем обрезанный кадр в формат RGB для отображения в QLabel
                cropped_frame_rgb = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)

                # Преобразуем обрезанный кадр в формат QImage
                cropped_height, cropped_width, _ = cropped_frame_rgb.shape
                cropped_q_image = QImage(cropped_frame_rgb.data, cropped_width, cropped_height, QImage.Format_RGB888)

                # Преобразуем QImage в формат QPixmap для отображения
                cropped_pixmap = QPixmap.fromImage(cropped_q_image)

                # Устанавливаем обрезанный pixmap на QLabel
                self.label.setPixmap(cropped_pixmap)

                return
            else:
                self.opacity_status(False)
        # Преобразуем кадр в формат RGB для отображения в QLabel
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Преобразуем кадр в формат QImage
        height, width, channel = frame_rgb.shape
        q_image = QImage(frame_rgb.data, width, height, QImage.Format_RGB888)

        # Преобразуем QImage в формат QPixmap для отображения
        pixmap = QPixmap.fromImage(q_image)

        # Устанавливаем pixmap на QLabel
        self.label.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Пример использования: создание прозрачного прямоугольника с красной границей
    rectangle = TransparentRectangle(0, 0, 500, 300, 2)
    rectangle.show()

    sys.exit(app.exec_())