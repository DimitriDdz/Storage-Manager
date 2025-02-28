from shutil import SameFileError

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from database import *


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.shelves, self.items = load_data()
        self.current_shelf = None
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Storage Manager")
        self.resize(1030, 600)
        self.setFixedSize(1030, 600)
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        layout = QHBoxLayout(self.centralwidget)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setFixedWidth(200)
        layout.addWidget(self.scroll_area, 1)
        self.main_area = QWidget()
        self.main_area_layout = QVBoxLayout(self.main_area)
        self.main_area_layout.setAlignment(Qt.AlignTop)
        self.buttons_widget = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_widget)
        self.add_button = QPushButton("+")
        self.add_button.clicked.connect(self.add_item)
        self.remove_button = QPushButton("-")
        self.remove_button.clicked.connect(self.remove_item)
        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.remove_button)
        self.main_area_layout.addWidget(self.buttons_widget)
        self.items_area = QScrollArea()
        self.items_area.setWidgetResizable(True)
        self.items_content = QWidget()
        self.items_layout = QGridLayout(self.items_content)
        self.items_layout.setAlignment(Qt.AlignTop)
        self.items_layout.setHorizontalSpacing(10)
        self.items_layout.setVerticalSpacing(10)
        self.items_area.setWidget(self.items_content)
        self.main_area_layout.addWidget(self.items_area)
        layout.addWidget(self.main_area, 3)
        self.menubar = self.menuBar()
        self.menu_create = self.menubar.addMenu("Создать")
        self.action_create_shelf = QAction("Создать полку", self)
        self.action_create_shelf.triggered.connect(self.create_shelf)
        self.action_delete_shelf = QAction("Удалить полку", self)
        self.action_delete_shelf.triggered.connect(self.delete_shelf)
        self.menu_create.addAction(self.action_create_shelf)
        self.menu_create.addAction(self.action_delete_shelf)

        self.menu_help = self.menubar.addMenu("Помощь")
        self.action_feedback = QAction("Обратная связь", self)
        self.action_feedback.triggered.connect(self.show_feedback_dialog)
        self.action_about = QAction("О программе", self)
        self.action_about.triggered.connect(self.show_about_dialog)
        self.menu_help.addAction(self.action_feedback)
        self.menu_help.addAction(self.action_about)

        self.update_shelves()

    def add_shelf_button(self, name):
        button = QPushButton(name)
        button.clicked.connect(lambda: self.shelf_clicked(name))
        self.scroll_layout.addWidget(button)

    def create_shelf(self):
        name, ok = QInputDialog.getText(self, "Создать полку", "Введите название (<=20 символов):")
        if ok:
            if name.lower() in [i.lower() for i in self.shelves]:
                QMessageBox.warning(self, "Ошибка", "Полка с таким названием уже существует!", QMessageBox.Ok)
                return
            if len(name) > 20:
                QMessageBox.warning(self, "Ошибка", "Название должно быть меньше 20 символов!", QMessageBox.Ok)
                return
            if len(name.replace(' ', '')) == 0 or len(name) == 0:
                QMessageBox.warning(self, "Ошибка", "Некорректное название!", QMessageBox.Ok)
                return
            self.shelves.append(name)
            self.shelves.sort()
            self.update_shelves()
            self.save_data()

    def delete_shelf(self):
        if not self.shelves:
            QMessageBox.information(self, "Удаление", "Нет доступных полок для удаления.", QMessageBox.Ok)
            return

        item, ok = QInputDialog.getItem(self, "Удалить полку", "Выберите полку:", self.shelves, 0, False)
        if ok and item:
            self.shelves.remove(item)
            if item in self.items:
                del self.items[item]
            self.update_shelves()
            self.save_data()

    def update_shelves(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        for shelf in sorted(self.shelves):
            self.add_shelf_button(shelf)

    def shelf_clicked(self, name):
        if self.current_shelf:
            for i in range(self.scroll_layout.count()):
                widget = self.scroll_layout.itemAt(i).widget()
                if isinstance(widget, QPushButton):
                    widget.setEnabled(True)
        self.current_shelf = name
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() == name:
                widget.setEnabled(False)
        self.update_items()

    def update_items(self):
        for i in reversed(range(self.items_layout.count())):
            widget = self.items_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if self.current_shelf and self.current_shelf in self.items:
            items = self.items[self.current_shelf]
            for idx, item in enumerate(items):
                row = idx // 2
                col = idx % 2
                self.items_layout.addWidget(self.create_item_widget(item), row, col)

    def create_item_widget(self, item):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)

        if item['image']:
            label = QLabel()
            pixmap = QPixmap(item['image'])
            label.setPixmap(pixmap.scaled(350, 350, Qt.KeepAspectRatio))
            layout.addWidget(label)

        name_label = QLabel(f"Название: {item['name']}")
        if int(item['quantity']) == 0:
            name_label.setStyleSheet("color: red;")
        layout.addWidget(name_label)

        quantity_label = QLabel(f"Количество: {item['quantity']}")
        layout.addWidget(quantity_label)

        edit_button = QPushButton("Редактировать")
        edit_button.clicked.connect(lambda: self.edit_item(item))
        layout.addWidget(edit_button)

        plus_button = QPushButton("+")
        plus_button.clicked.connect(lambda: self.change_quantity(item, 1))
        layout.addWidget(plus_button)

        minus_button = QPushButton("-")
        minus_button.clicked.connect(lambda: self.change_quantity(item, -1))
        layout.addWidget(minus_button)

        widget.setFixedSize(370, 370)
        return widget

    def change_quantity(self, item, delta):
        new_quantity = int(item['quantity']) + delta
        if new_quantity < 0:
            QMessageBox.warning(self, "Ошибка", "Количество не может быть отрицательным!", QMessageBox.Ok)
            return
        item['quantity'] = str(new_quantity)
        self.update_items()
        self.save_data()

    def add_item(self):
        if not self.current_shelf:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите полку!", QMessageBox.Ok)
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить предмет")
        layout = QVBoxLayout(dialog)

        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Название")
        layout.addWidget(name_edit)

        quantity_edit = QLineEdit()
        quantity_edit.setPlaceholderText("Количество")
        quantity_edit.setValidator(QIntValidator(0, 999999, self))
        layout.addWidget(quantity_edit)

        image_button = QPushButton("Загрузить картинку")
        image_path = None
        def load_image():
            nonlocal image_path
            image_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.bmp)")
        image_button.clicked.connect(load_image)
        layout.addWidget(image_button)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            name = name_edit.text()
            quantity = quantity_edit.text()
            if not name or not quantity:
                QMessageBox.warning(self, "Ошибка", "Название и количество обязательны!", QMessageBox.Ok)
                return

            if self.current_shelf not in self.items:
                self.items[self.current_shelf] = []

            if name.lower() in [item['name'].lower() for item in self.items[self.current_shelf]]:
                QMessageBox.warning(self, "Ошибка", "Предмет с таким названием уже существует на этой полке!", QMessageBox.Ok)
                return

            saved_image_path = save_image(image_path)  # Сохраняем изображение
            self.items[self.current_shelf].append({
                'name': name,
                'quantity': quantity,
                'image': saved_image_path
            })
            self.update_items()
            self.save_data()

    def edit_item(self, item):
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать предмет")
        layout = QVBoxLayout(dialog)

        name_edit = QLineEdit(item['name'])
        layout.addWidget(name_edit)

        quantity_edit = QLineEdit(item['quantity'])
        quantity_edit.setValidator(QIntValidator(0, 999999, self))
        layout.addWidget(quantity_edit)

        image_button = QPushButton("Загрузить новую картинку")
        image_path = item['image']
        def load_image():
            nonlocal image_path
            image_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.bmp)")
        image_button.clicked.connect(load_image)
        layout.addWidget(image_button)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            name = name_edit.text()
            quantity = quantity_edit.text()
            if not name or not quantity:
                QMessageBox.warning(self, "Ошибка", "Название и количество обязательны!", QMessageBox.Ok)
                return

            if name.lower() != item['name'].lower() and name.lower() in [i['name'].lower() for i in self.items[self.current_shelf]]:
                QMessageBox.warning(self, "Ошибка", "Предмет с таким названием уже существует на этой полке!", QMessageBox.Ok)
                return

            if item['image'] and item['image'] != image_path:
                delete_image(item['image'])

            try:
                saved_image_path = save_image(image_path)
            except SameFileError:
                pass
            item['name'] = name
            item['quantity'] = quantity
            try:
                item['image'] = saved_image_path
            except UnboundLocalError:
                pass
            self.update_items()
            self.save_data()

    def remove_item(self):
        if not self.current_shelf or self.current_shelf not in self.items or not self.items[self.current_shelf]:
            QMessageBox.warning(self, "Ошибка", "Нет предметов для удаления!", QMessageBox.Ok)
            return

        items = self.items[self.current_shelf]
        item_names = [item['name'] for item in items]
        item_name, ok = QInputDialog.getItem(self, "Удалить предмет", "Выберите предмет:", item_names, 0, False)
        if ok and item_name:
            item_to_remove = next(item for item in items if item['name'] == item_name)
            if item_to_remove['image']:
                delete_image(item_to_remove['image'])
            items.remove(item_to_remove)
            self.update_items()
            self.save_data()

    def save_data(self):
        """Сохраняет данные в файл."""
        save_data(self.shelves, self.items)

    def show_feedback_dialog(self):
        QMessageBox.information(self, "Обратная связь", """dsdudin@edu.hse.ru
Дудин Дмитрий Сергеевич""", QMessageBox.Ok)

    def show_about_dialog(self):
        QMessageBox.information(self, "О программе", "Рабочая программа", QMessageBox.Ok)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mainWin = Ui_MainWindow()
    mainWin.show()
    sys.exit(app.exec_())