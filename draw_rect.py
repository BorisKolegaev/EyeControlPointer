import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor


class TransparentRectangle(QWidget):
    def __init__(self, left, top, width, height, border_width):
        super().__init__()

        # Set the window attributes for transparency and no click-through
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setWindowOpacity(0.5)

        # Set the size and position of the rectangle
        self.setGeometry(left, top, width, height)

        # Store the border width
        self.border_width = border_width

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.red)
        pen.setWidth(self.border_width)
        #pen.setColor("red")
        painter.setPen(pen)

        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Example usage: create a transparent rectangle with visible borders
    rectangle = TransparentRectangle(100, 100, 500, 300, 2)
    rectangle.show()

    sys.exit(app.exec_())