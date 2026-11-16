import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QApplication
from database import init_db
from ui import NoteFlowWindow
from controller import NoteController  # Импортируем контроллер


def main():

    app = QApplication(sys.argv)

    # 1. Создаем окно
    window = NoteFlowWindow()

    # 2. Создаем контроллер и передаем ему окно для управления
    controller = NoteController(window)

    # 3. Показываем окно
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()