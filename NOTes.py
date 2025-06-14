import json
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLineEdit, QMessageBox, QDialog, QTextEdit, QLabel, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty, QEasingCurve
from PyQt6.QtGui import QColor

NOTES_FILE = 'notes.json'

def load_notes():
    if not os.path.exists(NOTES_FILE):
        return []
    with open(NOTES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_notes(notes):
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

class AnimatedButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self._bg_color = QColor("#3A7BD5")
        self._animation = QPropertyAnimation(self, b"bgColor", self)
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.setStyleSheet(self._get_stylesheet(self._bg_color))

    def _get_stylesheet(self, color):
        return f"""
            QPushButton {{
                background-color: {color.name()};
                color: white;
                border-radius: 10px;
                padding: 8px 16px;
                font-weight: 600;
                min-width: 90px;
            }}
        """

    def getBgColor(self):
        return self._bg_color

    def setBgColor(self, color):
        if isinstance(color, QColor):
            self._bg_color = color
            self.setStyleSheet(self._get_stylesheet(color))

    bgColor = pyqtProperty(QColor, fget=getBgColor, fset=setBgColor)

    def enterEvent(self, event):
        self._animate_color(QColor("#5599FF"))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_color(QColor("#3A7BD5"))
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._animate_color(QColor("#2A5CA8"))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._animate_color(QColor("#5599FF"))
        super().mouseReleaseEvent(event)

    def _animate_color(self, target_color):
        self._animation.stop()
        self._animation.setStartValue(self._bg_color)
        self._animation.setEndValue(target_color)
        self._animation.start()

class NoteDialog(QDialog):
    def __init__(self, parent=None, note=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование заметки" if note else "Создание заметки")
        self.resize(450, 350)

        self.setStyleSheet("""
            QDialog {
                background-color: #2c2f33;
            }
            QLabel {
                font-weight: 600;
                font-size: 14px;
                color: #ddd;
            }
            QTextEdit {
                border: 1px solid #444;
                border-radius: 6px;
                font-size: 13px;
                padding: 6px;
                background-color: #23272a;
                color: #eee;
            }
            QLineEdit {
                border: 1px solid #444;
                border-radius: 6px;
                font-size: 13px;
                padding: 6px;
                background-color: #23272a;
                color: #eee;
            }
            QDialogButtonBox QPushButton {
                min-width: 80px;
                padding: 6px 12px;
                font-weight: 600;
                border-radius: 6px;
                background-color: #3A7BD5;
                color: white;
            }
            QDialogButtonBox QPushButton:pressed {
                background-color: #2A5CA8;
            }
        """)

        self.text_edit = QTextEdit()
        self.tags_edit = QLineEdit()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Текст заметки:"))
        layout.addWidget(self.text_edit)
        layout.addWidget(QLabel("Теги (через запятую):"))
        layout.addWidget(self.tags_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

        if note:
            self.text_edit.setPlainText(note['text'])
            self.tags_edit.setText(", ".join(note['tags']))

    def get_data(self):
        text = self.text_edit.toPlainText().strip()
        tags = [tag.strip().lower() for tag in self.tags_edit.text().split(',') if tag.strip()]
        return text, tags

class NotesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Заметки с тегами")
        self.resize(640, 480)

        self.notes = load_notes()

        self.setStyleSheet("""
            QWidget {
                background-color: #23272a;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
                color: #ddd;
            }
            QLineEdit#searchEdit {
                border: 2px solid #3A7BD5;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #2c2f33;
                color: #eee;
            }
            QListWidget {
                background-color: #2c2f33;
                border-radius: 12px;
                border: 1px solid #444;
                padding: 6px;
                color: #eee;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background-color: #3A7BD5;
                color: white;
                border-radius: 8px;
            }
            QLabel#titleLabel {
                font-size: 20px;
                font-weight: 700;
                margin-bottom: 10px;
                color: #eee;
            }
        """)

        main_layout = QVBoxLayout()
        header_layout = QHBoxLayout()

        title_label = QLabel("Заметки с тегами")
        title_label.setObjectName("titleLabel")

        header_layout.addWidget(title_label)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("searchEdit")
        self.search_edit.setPlaceholderText("Поиск заметок по тексту и тегам...")
        self.search_edit.textChanged.connect(self.update_list)
        search_layout.addWidget(self.search_edit)
        main_layout.addLayout(search_layout)

        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.btn_create = AnimatedButton("Создать")
        self.btn_edit = AnimatedButton("Редактировать")
        self.btn_delete = AnimatedButton("Удалить")

        self.btn_create.clicked.connect(self.create_note)
        self.btn_edit.clicked.connect(self.edit_note)
        self.btn_delete.clicked.connect(self.delete_note)

        btn_layout.addWidget(self.btn_create)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)

        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        self.update_list()

    def update_list(self):
        query = self.search_edit.text().lower()
        self.list_widget.clear()
        for note in self.notes:
            text = note['text']
            tags = ", ".join(note['tags'])
            display = f"{note['id']}: {text[:50]}{'...' if len(text) > 50 else ''} [{tags}]"
            if query in text.lower() or any(query in tag for tag in note['tags']):
                self.list_widget.addItem(display)

    def get_selected_index(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Внимание", "Выберите заметку в списке.")
            return None
        note_id = int(current_item.text().split(":")[0])
        for i, note in enumerate(self.notes):
            if note['id'] == note_id:
                return i
        return None

    def create_note(self):
        dialog = NoteDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            text, tags = dialog.get_data()
            if not text:
                QMessageBox.warning(self, "Внимание", "Текст заметки не может быть пустым.")
                return
            new_id = max((note['id'] for note in self.notes), default=0) + 1
            self.notes.append({'id': new_id, 'text': text, 'tags': tags})
            save_notes(self.notes)
            self.update_list()

    def edit_note(self):
        idx = self.get_selected_index()
        if idx is None:
            return
        note = self.notes[idx]
        dialog = NoteDialog(self, note)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            text, tags = dialog.get_data()
            if not text:
                QMessageBox.warning(self, "Внимание", "Текст заметки не может быть пустым.")
                return
            self.notes[idx]['text'] = text
            self.notes[idx]['tags'] = tags
            save_notes(self.notes)
            self.update_list()

    def delete_note(self):
        idx = self.get_selected_index()
        if idx is None:
            return
        reply = QMessageBox.question(self, "Удалить", "Вы действительно хотите удалить заметку?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.notes.pop(idx)
            save_notes(self.notes)
            self.update_list()

if __name__ == "__main__":
    app = QApplication([])
    window = NotesApp()
    window.show()
    app.exec()
