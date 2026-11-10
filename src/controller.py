from PyQt6.QtWidgets import QMessageBox, QListWidgetItem, QListWidget
from PyQt6.QtCore import Qt
import database as db
from ui import NoteItemWidget


class NoteController:
    def __init__(self, ui_window):
        self.ui = ui_window
        self.current_note_id = None

        # Подключение кнопок и событий
        self.ui.btn_new_note.clicked.connect(self.create_new_note)
        self.ui.notes_list.itemClicked.connect(self.load_selected_note)

        # Автосохранение
        self.ui.title_input.textChanged.connect(self.auto_save)
        self.ui.text_edit.textChanged.connect(self.auto_save)

        # Поиск
        self.ui.search_input.textChanged.connect(self.refresh_notes_list)

        # Меню и горячие клавиши
        self.ui.action_new.triggered.connect(self.create_new_note)
        self.ui.action_save.triggered.connect(self.force_save)
        self.ui.action_delete.triggered.connect(self.delete_current_note)

        # Удаление по клавише Delete в списке
        self.ui.notes_list.keyPressEvent = self.list_key_press_event

        self.refresh_notes_list()

    def refresh_notes_list(self):
        print("--- ОБНОВЛЕНИЕ СПИСКА ЗАМЕТОК ---")
        """Обновляет список заметок в левой панели (с учетом поиска)."""
        self.ui.notes_list.clear()
        search_text = self.ui.search_input.text().lower()
        notes = db.get_all_notes()

        for note_id, title in notes:
            if search_text and search_text not in title.lower():
                continue

            # Создаем элемент списка
            item = QListWidgetItem(self.ui.notes_list)
            # Создаем наш кастомный виджет (текст + крестик)
            widget = NoteItemWidget(note_id, title)

            # Сохраняем ID заметки
            item.setData(Qt.ItemDataRole.UserRole, note_id)

            # Устанавливаем размер элемента и помещаем в него виджет
            item.setSizeHint(widget.sizeHint())
            self.ui.notes_list.setItemWidget(item, widget)

            # Подключаем крестик к функции удаления
            widget.btn_delete.clicked.connect(lambda checked, nid=note_id: self.delete_note_by_id(nid))

    def create_new_note(self):
        new_id = db.create_note("Новая заметка", "")
        self.refresh_notes_list()
        for i in range(self.ui.notes_list.count()):
            item = self.ui.notes_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == new_id:
                self.ui.notes_list.setCurrentItem(item)
                self.load_selected_note(item)
                break

    def load_selected_note(self, item):
        note_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_note_id = note_id
        note_data = db.get_note_by_id(note_id)

        if note_data:
            title, content = note_data
            self.ui.title_input.blockSignals(True)
            self.ui.text_edit.blockSignals(True)
            self.ui.title_input.setText(title)
            self.ui.text_edit.setText(content)
            self.ui.title_input.blockSignals(False)
            self.ui.text_edit.blockSignals(False)
            self.update_status_bar()

    def auto_save(self):
        if self.current_note_id is None:
            return
        title = self.ui.title_input.text().strip() or "Без названия"
        content = self.ui.text_edit.toPlainText()
        db.update_note(self.current_note_id, title, content)

        # Обновляем название в списке (внутри кастомного виджета)
        for i in range(self.ui.notes_list.count()):
            item = self.ui.notes_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == self.current_note_id:
                # Достаем наш кастомный виджет из элемента списка
                widget = self.ui.notes_list.itemWidget(item)
                if widget:
                    # Меняем текст внутри QLabel этого виджета
                    widget.label.setText(title)
                break
        self.update_status_bar()

    def force_save(self):
        self.auto_save()
        self.ui.status_bar.showMessage("Успешно сохранено!", 3000)

    def update_status_bar(self):
        text = self.ui.text_edit.toPlainText()
        chars = len(text)
        words = len(text.split())
        self.ui.status_bar.showMessage(f"Сохранено | Символов: {chars} | Слов: {words}")

    def list_key_press_event(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.delete_current_note()
        else:
            QListWidget.keyPressEvent(self.ui.notes_list, event)

    def delete_current_note(self):
        if self.current_note_id is None:
            return
        reply = QMessageBox.question(
            self.ui, 'Удаление', 'Вы уверены, что хотите удалить эту заметку?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            db.delete_note(self.current_note_id)
            self.current_note_id = None
            self.ui.title_input.clear()
            self.ui.text_edit.clear()
            self.refresh_notes_list()
            self.ui.status_bar.showMessage("Заметка удалена")

    def delete_note_by_id(self, note_id):
        """Удаляет заметку по её ID (вызывается при клике на крестик)."""
        reply = QMessageBox.question(
            self.ui, 'Удаление',
            'Вы уверены, что хотите удалить эту заметку?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            db.delete_note(note_id)

            # Если удалили открытую заметку, очищаем редактор
            if self.current_note_id == note_id:
                self.current_note_id = None
                self.ui.title_input.clear()
                self.ui.text_edit.clear()

            self.refresh_notes_list()
            self.ui.status_bar.showMessage("Заметка удалена")