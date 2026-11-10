import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QListWidget, QLineEdit, QTextEdit,
                             QStatusBar, QToolBar, QPushButton, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction  # Обязательно импортируем QAction для меню


class NoteItemWidget(QWidget):
    """Кастомный виджет для строки в списке заметок (текст + кнопка удаления)."""

    def __init__(self, note_id, title, parent=None):
        super().__init__(parent)
        self.note_id = note_id

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # Текст заметки
        self.label = QLabel(title)
        self.label.setStyleSheet("background: transparent;")

        # Кнопка-крестик
        self.btn_delete = QPushButton("X") # Используем обычную английскую X
        self.btn_delete.setFixedSize(30, 30) # Делаем кнопку больше
        self.btn_delete.setToolTip("Удалить заметку")
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: red;  /* Ярко-красный фон */
                color: white;
                border: 1px solid white; /* Белая рамка для контраста */
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)

        layout.addWidget(self.label)
        layout.addStretch()  # Прижимаем крестик к правому краю
        layout.addWidget(self.btn_delete)


class NoteFlowWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Настройка главного окна (по ТЗ: 800x600, Заголовок)
        self.setWindowTitle("NoteFlow — Менеджер заметок")
        self.resize(800, 600)

        # 2. Настройка шрифтов (по ТЗ: Segoe UI, 10pt для интерфейса)
        font = QFont("Segoe UI", 10)
        self.setFont(font)

        # 3. Создание центрального виджета
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # =================================================================
        # 4. СОЗДАНИЕ МЕНЮ (Верхняя панель File, Edit, Help)
        # Именно этого блока не хватало контроллеру!
        # =================================================================
        menubar = self.menuBar()

        # Меню File
        file_menu = menubar.addMenu('File')

        self.action_new = QAction('Новая заметка', self)
        self.action_new.setShortcut('Ctrl+N')
        file_menu.addAction(self.action_new)

        self.action_save = QAction('Сохранить', self)
        self.action_save.setShortcut('Ctrl+S')
        file_menu.addAction(self.action_save)

        action_exit = QAction('Выход', self)
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_exit)

        # Меню Edit
        edit_menu = menubar.addMenu('Edit')
        self.action_delete = QAction('Удалить заметку', self)
        self.action_delete.setShortcut('Delete')
        edit_menu.addAction(self.action_delete)
        # =================================================================

        # 5. Верхняя часть: Тулбар со строкой поиска и кнопкой
        self.toolbar = QToolBar("Основные действия")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        # Строка поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по заметкам...")
        self.search_input.setFixedWidth(300)
        self.toolbar.addWidget(self.search_input)

        # Кнопка "Новая заметка"
        self.btn_new_note = QPushButton("Новая заметка")
        self.toolbar.addWidget(self.btn_new_note)

        # 6. Центральная часть: QSplitter (разделяет экран на две части)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Левая зона: Список заметок ---
        self.notes_list = QListWidget()
        self.splitter.addWidget(self.notes_list)

        # --- Правая зона: Редактор ---
        self.editor_widget = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_widget)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы

        # Поле для заголовка заметки
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Заголовок заметки...")
        title_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        self.title_input.setFont(title_font)

        # Текстовое поле для самой заметки
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Текст заметки...")

        self.editor_layout.addWidget(self.title_input)
        self.editor_layout.addWidget(self.text_edit)

        self.splitter.addWidget(self.editor_widget)

        # Настраиваем пропорции: слева 1 часть, справа 3 части
        self.splitter.setSizes([200, 600])

        # Добавляем сплиттер в главный слой
        self.main_layout.addWidget(self.splitter)

        # 7. Нижняя часть: Статус-бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово к работе | Символов: 0 | Слов: 0")

        # 8. Настройка стилей (CSS) чтобы выглядело современно
        self.apply_styles()

    def apply_styles(self):
        """Применяет QSS стили для красивого внешнего вида."""
        style_sheet = """
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                color: #ffffff;
            }
            QLineEdit, QTextEdit, QListWidget {
                background-color: #3c3f41;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #007acc;
            }
            QListWidget::item:selected {
                background-color: #007acc;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
            QToolBar {
                background-color: #1e1e1e;
                padding: 5px;
                spacing: 10px;
            }
            QStatusBar {
                background-color: #1e1e1e;
                color: #aaaaaa;
            }
        """
        self.setStyleSheet(style_sheet)