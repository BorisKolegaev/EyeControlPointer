import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QPixmap


class TransparentRectangle(QWidget):
    def __init__(self, left, top, width, height, border_width):
        super().__init__()

        # Set the window attributes for transparency and no click-through
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setWindowOpacity(1)

        # Set the size and position of the rectangle
        self.setGeometry(left, top, width, height)

        # Store the border width
        self.border_width = border_width

    def update_frame(self, frame):
        # Convert the frame to QImage format
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        # Update the frame inside the widget
        self.setPixmap(QPixmap.fromImage(q_image))

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(0xFF, 0, 0, 0x80))
        pen.setWidth(self.border_width)
        #pen.setColor("red")
        painter.setPen(pen)

        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Example usage: create a transparent rectangle with visible borders
    rectangle = TransparentRectangle(100, 100, 500, 300, 35)
    rectangle.show()

    sys.exit(app.exec_())