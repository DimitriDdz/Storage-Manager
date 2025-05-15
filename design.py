from shutil import SameFileError
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from database import *
import pandas as pd
import openpyxl

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.shelves, self.items, self.archive, self.clients = load_data()
        self.current_shelf = None
        self.dark_theme = False
        self.setupUi()
        self.apply_theme()
        self.check_archive_expiry()
        self.setStyleSheet("""
            QWidget {
                font-family: Arial;
                font-size: 14px;
            }

            QGroupBox {
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                margin-top: 10px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }

            QPushButton {
                background-color: #2a8d9c;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }

            QPushButton:hover {
                background-color: #2980b9;
            }

            QLineEdit, QComboBox, QSpinBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }

            QTableWidget {
                gridline-color: #ddd;
                border: 1px solid #ccc;
            }

            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #ccc;
            }
        """)

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

        self.add_button = QPushButton("Добавить предмет")
        self.add_button.clicked.connect(self.add_item)
        self.remove_button = QPushButton("Удалить предмет")
        self.remove_button.clicked.connect(self.remove_item)
        self.search_button = QPushButton("Поиск")
        self.search_button.clicked.connect(self.show_search_dialog)

        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.remove_button)
        self.buttons_layout.addWidget(self.search_button)

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

        self.menu_edit = self.menubar.addMenu("Редактировать полки")
        self.action_create_shelf = QAction("Создать полку", self)
        self.action_create_shelf.triggered.connect(self.create_shelf)
        self.action_delete_shelf = QAction("Удалить полку", self)
        self.action_delete_shelf.triggered.connect(self.delete_shelf)
        self.menu_edit.addAction(self.action_create_shelf)
        self.menu_edit.addAction(self.action_delete_shelf)

        self.menu_analytics = self.menubar.addMenu("Аналитика")
        self.action_show_dashboard = QAction("Показать дашборд", self)
        self.action_show_dashboard.triggered.connect(self.show_analytics_dashboard)
        self.menu_analytics.addAction(self.action_show_dashboard)

        self.menu_view = self.menubar.addMenu("Вид")
        self.action_toggle_theme = QAction("Переключить тему", self)
        self.action_toggle_theme.triggered.connect(self.toggle_theme)
        self.menu_view.addAction(self.action_toggle_theme)

        self.menu_sort = self.menu_view.addMenu("Сортировка")

        self.action_sort_name = QAction("По названию", self)
        self.action_sort_name.triggered.connect(lambda: self.set_sort_mode('name'))
        self.menu_sort.addAction(self.action_sort_name)

        self.action_sort_quantity = QAction("По количеству", self)
        self.action_sort_quantity.triggered.connect(lambda: self.set_sort_mode('quantity'))
        self.menu_sort.addAction(self.action_sort_quantity)

        self.action_sort_date = QAction("По дате добавления", self)
        self.action_sort_date.triggered.connect(lambda: self.set_sort_mode('date'))
        self.menu_sort.addAction(self.action_sort_date)

        self.menu_help = self.menubar.addMenu("Помощь")
        self.action_feedback = QAction("Обратная связь", self)
        self.action_feedback.triggered.connect(self.show_feedback_dialog)
        self.action_about = QAction("О программе", self)
        self.action_about.triggered.connect(self.show_about_dialog)
        self.action_archive = QAction("Архив", self)
        self.action_archive.triggered.connect(self.show_archive_dialog)
        self.menu_help.addAction(self.action_feedback)
        self.menu_help.addAction(self.action_about)
        self.menu_help.addAction(self.action_archive)

        self.sort_mode = 'name'
        self.update_shelves()

    def apply_theme(self):
        if self.dark_theme:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                }
                QWidget {
                    font-family: Arial;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #3D3D3D;
                    border: 1px solid #555;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #4D4D4D;
                }
                QPushButton:disabled {
                    background-color: #333;
                }
                QLineEdit, QComboBox {
                    background-color: #3D3D3D;
                    border: 1px solid #555;
                    color: #FFFFFF;
                }
                QLabel {
                    color: #FFFFFF;
                }
                QScrollArea {
                    border: none;
                }
                QMenuBar {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                }
                QMenuBar::item:selected {
                    background-color: #4D4D4D;
                }
                QMenu {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                }
                QMenu::item:selected {
                    background-color: #4D4D4D;
                }
            """)
        else:
            self.setStyleSheet("""
                        QWidget {
                            font-family: Arial;
                            font-size: 14px;
                        }

                        QGroupBox {
                            border: 1px solid #dcdcdc;
                            border-radius: 5px;
                            margin-top: 10px;
                        }

                        QGroupBox::title {
                            subcontrol-origin: margin;
                            left: 10px;
                            padding: 0 5px;
                        }

                        QPushButton {
                            background-color: #2a8d9c;
                            color: white;
                            padding: 5px;
                            border-radius: 5px;
                        }

                        QPushButton:hover {
                            background-color: #2980b9;
                        }

                        QLineEdit, QComboBox, QSpinBox {
                            padding: 5px;
                            border: 1px solid #ccc;
                            border-radius: 4px;
                        }

                        QTableWidget {
                            gridline-color: #ddd;
                            border: 1px solid #ccc;
                        }

                        QHeaderView::section {
                            background-color: #f0f0f0;
                            padding: 4px;
                            border: 1px solid #ccc;
                        }
                    """)

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.apply_theme()

    def set_sort_mode(self, mode):
        self.sort_mode = mode
        if self.current_shelf:
            self.update_items()

    def show_analytics_dashboard(self):
        self.dashboard = AnalyticsDashboard(
            self.items,
            self.clients,
            lambda: Ui_MainWindow.save_data(
                self.shelves,
                self.items,
                self.archive,
                self.clients
            ),
            parent_window=self
        )
        self.dashboard.show()

    def add_shelf_button(self, name):
        item_count = len(self.items.get(name, []))
        total_quantity = sum(int(item['quantity']) for item in self.items.get(name, []))

        button = QPushButton(f"{name} {item_count}/{total_quantity}")
        button.clicked.connect(lambda: self.shelf_clicked(name))
        self.scroll_layout.addWidget(button)

    def show_search_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Поиск предмета")
        dialog.resize(600, 400)

        layout = QVBoxLayout(dialog)

        search_edit = QLineEdit()
        search_edit.setPlaceholderText("Введите название предмета...")
        layout.addWidget(search_edit)

        self.search_results = QListWidget()
        layout.addWidget(self.search_results)

        search_edit.textChanged.connect(lambda: self.perform_search(search_edit.text()))

        self.search_results.itemDoubleClicked.connect(lambda: self.go_to_item(self.search_results.currentItem()))

        dialog.exec_()

    def perform_search(self, query):
        self.search_results.clear()
        if not query.strip():
            return

        query = query.lower()
        for shelf_name, items in self.items.items():
            for item in items:
                item_name = item['name'].lower()
                if query in item_name:
                    item_widget = QListWidgetItem(f"{item['name']} (Кол-во: {item['quantity']}) - Полка: {shelf_name}")
                    item_widget.setData(Qt.UserRole, (shelf_name, item['name']))
                    self.search_results.addItem(item_widget)

    def go_to_item(self, item):
        shelf_name, item_name = item.data(Qt.UserRole)
        self.shelf_clicked(shelf_name)


        for i in range(self.items_layout.count()):
            widget = self.items_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'item_name') and widget.item_name == item_name:
                self.items_area.ensureWidgetVisible(widget)
                break

    def restore_from_archive(self):
        if not self.archive_list.currentItem():
            return

        item_data = self.archive_list.currentItem().data(Qt.UserRole)

        shelf, ok = QInputDialog.getItem(self, "Восстановление", "Выберите полку для восстановления:",
                                         self.shelves, 0, False)
        if ok and shelf:
            if shelf not in self.items:
                self.items[shelf] = []

            if any(i['name'].lower() == item_data['name'].lower() for i in self.items[shelf]):
                QMessageBox.warning(self, "Ошибка", "Предмет с таким названием уже есть на этой полке!")
                return

            self.items[shelf].append({
                'name': item_data['name'],
                'quantity': item_data['quantity'],
                'image': item_data.get('image', ''),
                'date_added': datetime.now().isoformat()
            })

            self.archive.remove(item_data)
            self.save_data(self.shelves, self.items, self.archive, self.clients)

            self.shelf_clicked(shelf)


            self.archive_dialog.close()

            QMessageBox.information(self, "Успех", "Предмет восстановлен!")
            self.update_shelves()

    def delete_from_archive(self):
        if not self.archive_list.currentItem():
            return

        item_data = self.archive_list.currentItem().data(Qt.UserRole)

        if item_data.get('image'):
            delete_image(item_data['image'])

        self.archive.remove(item_data)
        self.save_data(self.shelves, self.items, self.archive, self.clients)

        self.archive_dialog.close()

        QMessageBox.information(self, "Удалено", "Предмет окончательно удален из архива!")

    def show_archive_dialog(self):
        self.archive_dialog = QDialog(self)
        self.archive_dialog.setWindowTitle("Архив")
        self.archive_dialog.resize(600, 400)

        layout = QVBoxLayout(self.archive_dialog)

        if not self.archive:
            label = QLabel("Архив пуст")
            layout.addWidget(label)

            close_button = QPushButton("Закрыть")
            close_button.clicked.connect(self.archive_dialog.close)
            layout.addWidget(close_button)
        else:
            self.archive_list = QListWidget()
            layout.addWidget(self.archive_list)

            for item in self.archive:
                item_widget = QListWidgetItem(
                    f"{item['name']} (Было: {item['quantity']}) - Удален с: {item.get('shelf', 'Неизвестно')}")
                item_widget.setData(Qt.UserRole, item)
                self.archive_list.addItem(item_widget)

            buttons_layout = QHBoxLayout()

            restore_button = QPushButton("Восстановить")
            restore_button.clicked.connect(self.restore_from_archive)
            buttons_layout.addWidget(restore_button)

            delete_button = QPushButton("Удалить навсегда")
            delete_button.clicked.connect(self.delete_from_archive)
            buttons_layout.addWidget(delete_button)

            close_button = QPushButton("Закрыть")
            close_button.clicked.connect(self.archive_dialog.close)
            buttons_layout.addWidget(close_button)

            layout.addLayout(buttons_layout)

        self.archive_dialog.exec_()


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
            self.save_data(self.shelves, self.items, self.archive, self.clients)

    def delete_shelf(self):
        if not self.shelves:
            QMessageBox.information(self, "Удаление", "Нет доступных полок для удаления.", QMessageBox.Ok)
            return

        item, ok = QInputDialog.getItem(self, "Удалить полку", "Выберите полку:", self.shelves, 0, False)
        if ok and item:
            if item in self.items:
                for product in self.items[item]:
                    product['shelf'] = item
                    self.archive.append(product)

                for product in self.items[item]:
                    if product.get('image'):
                        delete_image(product['image'])

                del self.items[item]

            self.shelves.remove(item)
            self.update_shelves()
            self.save_data(self.shelves, self.items, self.archive, self.clients)

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
            if isinstance(widget, QPushButton) and widget.text().startswith(name):
                widget.setEnabled(False)
        self.update_items()

    def update_items(self):
        for i in reversed(range(self.items_layout.count())):
            widget = self.items_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if self.current_shelf and self.current_shelf in self.items:
            items = self.items[self.current_shelf]

            if self.sort_mode == 'name':
                items = sorted(items, key=lambda x: x['name'])
            elif self.sort_mode == 'quantity':
                items = sorted(items, key=lambda x: int(x['quantity']), reverse=True)
            elif self.sort_mode == 'date':
                items = sorted(items, key=lambda x: x.get('date_added', ''), reverse=True)

            for idx, item in enumerate(items):
                row = idx // 2
                col = idx % 2
                widget = self.create_item_widget(item)
                widget.item_name = item['name']
                self.items_layout.addWidget(widget, row, col)

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

        if 'date_added' in item:
            date_label = QLabel(f"Добавлен: {item['date_added'][:10]}")
            layout.addWidget(date_label)

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
        self.update_shelves()
        self.save_data(self.shelves, self.items, self.archive, self.clients)

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
                QMessageBox.warning(self, "Ошибка", "Предмет с таким названием уже существует на этой полке!",
                                    QMessageBox.Ok)
                return

            saved_image_path = save_image(image_path)
            self.items[self.current_shelf].append({
                'name': name,
                'quantity': quantity,
                'image': saved_image_path,
                'date_added': datetime.now().isoformat()
            })
            self.update_items()
            self.update_shelves()
            self.save_data(self.shelves, self.items, self.archive, self.clients)

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

            if name.lower() != item['name'].lower() and name.lower() in [i['name'].lower() for i in
                                                                         self.items[self.current_shelf]]:
                QMessageBox.warning(self, "Ошибка", "Предмет с таким названием уже существует на этой полке!",
                                    QMessageBox.Ok)
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
            self.update_shelves()
            self.save_data(self.shelves, self.items, self.archive, self.clients)

    def check_archive_expiry(self):
        now = datetime.now()
        expired_items = []

        for item in self.archive:
            if 'date_deleted' not in item:
                continue

            deleted_date = datetime.fromisoformat(item['date_deleted'])
            if (now - deleted_date).days > 5:
                expired_items.append(item)

        for item in expired_items:
            if item.get('image'):
                delete_image(item['image'])
            self.archive.remove(item)

        if expired_items:
            self.save_data(self.shelves, self.items, self.archive, self.clients)

    def remove_item(self):
        if not self.current_shelf or self.current_shelf not in self.items or not self.items[self.current_shelf]:
            QMessageBox.warning(self, "Ошибка", "Нет предметов для удаления!", QMessageBox.Ok)
            return

        items = self.items[self.current_shelf]
        item_names = [item['name'] for item in items]
        item_name, ok = QInputDialog.getItem(self, "Удалить предмет", "Выберите предмет:", item_names, 0, False)
        if ok and item_name:
            item_to_remove = next(item for item in items if item['name'] == item_name)

            item_to_remove['date_deleted'] = datetime.now().isoformat()
            item_to_remove['shelf'] = self.current_shelf
            self.archive.append(item_to_remove)

            items.remove(item_to_remove)
            self.update_items()
            self.update_shelves()
            self.save_data(self.shelves, self.items, self.archive, self.clients)
            self.check_archive_expiry()

    @staticmethod
    def save_data(shelves, items, archive, clients):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "shelves": shelves,
                "items": items,
                "archive": archive,
                "clients": clients
            }, f, indent=4, ensure_ascii=False)

    def show_feedback_dialog(self):
        QMessageBox.information(self, "Обратная связь", """dsdudin@edu.hse.ru
Дудин Дмитрий Сергеевич""", QMessageBox.Ok)

    def show_about_dialog(self):
        QMessageBox.information(self, "О программе", "Рабочая программа", QMessageBox.Ok)


class AnalyticsDashboard(QWidget):
    def __init__(self, items_data, clients, save_data_func, parent_window=None):
        super().__init__()
        self.items = items_data
        self.clients = clients
        self.save_data_func = save_data_func
        self.parent_window = parent_window
        self.setWindowTitle("Аналитика склада")
        self.resize(1000, 700)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout()

        metrics_group = QGroupBox("Ключевые показатели")
        metrics_layout = QHBoxLayout()

        self.total_items_label = self.create_metric_card("Всего позиций", "0")
        self.total_quantity_label = self.create_metric_card("Общее количество", "0")

        metrics_layout.addWidget(self.total_items_label)
        metrics_layout.addWidget(self.total_quantity_label)
        metrics_group.setLayout(metrics_layout)
        main_layout.addWidget(metrics_group)


        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Полка", "Товар", "Количество", "Дата"])
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.table_widget)

        export_button = QPushButton("Экспорт в Excel")
        export_button.clicked.connect(self.export_to_excel)
        main_layout.addWidget(export_button)

        self.clients_button = QPushButton("Клиенты")
        self.clients_button.clicked.connect(self.show_clients_window)
        main_layout.addWidget(self.clients_button)


        self.setLayout(main_layout)

    def show_clients_window(self):
        self.clients_win = ClientsWindow(
            self.items,
            self.clients,
            lambda: Ui_MainWindow.save_data(
                self.parent_window.shelves,
                self.items,
                self.parent_window.archive,
                self.clients
            )
        )
        self.clients_win.show()

    def export_to_excel(self):
        try:
            export_data = []
            for shelf, items in self.items.items():
                for item in items:
                    export_data.append({
                        "Полка": shelf,
                        "Название": item.get("name", ""),
                        "Количество": item.get("quantity", ""),
                        "Дата добавления": item.get("date_added", ""),
                    })

            if not export_data:
                QMessageBox.information(self, "Экспорт", "Нет данных для экспорта.")
                return

            df = pd.DataFrame(export_data)
            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить Excel", "", "Excel Files (*.xlsx)")
            if file_path:
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Экспорт завершён", f"Данные успешно сохранены в {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте: {str(e)}")

    def create_metric_card(self, title, value):
        group = QGroupBox(title)
        layout = QVBoxLayout()
        label = QLabel(value)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        group.setLayout(layout)
        return group

    def load_data(self):
        try:
            self.total_items = sum(len(items) for items in self.items.values())
            self.total_quantity = sum(int(item['quantity']) for shelf in self.items.values() for item in shelf)

            self.total_items_label.findChild(QLabel).setText(str(self.total_items))
            self.total_quantity_label.findChild(QLabel).setText(str(self.total_quantity))

            self.update_plots()
            self.update_table()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def update_plots(self):
        try:
            self.figure.clear()

            ax1 = self.figure.add_subplot(121)
            shelves = list(self.items.keys())
            item_quantities = [sum(int(item['quantity']) for item in self.items[shelf]) for shelf in shelves]

            bars = ax1.bar(shelves, item_quantities, color='skyblue')
            ax1.set_title("Количество предметов по полкам")
            ax1.set_ylabel("Количество")
            ax1.tick_params(axis='x', rotation=45)

            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width() / 2., height,
                         f'{int(height)}',
                         ha='center', va='bottom')

            ax2 = self.figure.add_subplot(122)
            monthly_data = self.get_monthly_stats()

            if monthly_data:
                dates = list(monthly_data.keys())
                counts = list(monthly_data.values())

                ax2.plot(dates, counts, marker='o', linestyle='-', color='green')
                ax2.set_title("Новые позиции по месяцам")
                ax2.set_ylabel("Количество")
                ax2.tick_params(axis='x', rotation=45)

                for i, count in enumerate(counts):
                    ax2.text(dates[i], count, f'{count}', ha='center', va='bottom')
            else:
                ax2.text(0.5, 0.5, "Нет данных по датам",
                         ha='center', va='center', fontsize=12)

            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            print(f"Ошибка при обновлении графиков: {e}")

    def get_monthly_stats(self):
        monthly = {}
        try:
            for shelf in self.items.values():
                for item in shelf:
                    if 'date_added' in item and item['date_added']:
                        try:
                            month = datetime.fromisoformat(item['date_added']).strftime("%Y-%m")
                            monthly[month] = monthly.get(month, 0) + 1
                        except ValueError:
                            continue
            return dict(sorted(monthly.items()))
        except:
            return {}

    def update_table(self):
        try:
            self.table_widget.setRowCount(0)
            row_count = 0
            for shelf, items in self.items.items():
                for item in items:
                    self.table_widget.insertRow(row_count)

                    self.table_widget.setItem(row_count, 0, QTableWidgetItem(shelf))
                    self.table_widget.setItem(row_count, 1, QTableWidgetItem(item['name']))
                    self.table_widget.setItem(row_count, 2, QTableWidgetItem(str(item['quantity'])))
                    self.table_widget.setItem(row_count, 3, QTableWidgetItem(item.get('date_added', '')))
                    row_count += 1

            self.table_widget.resizeColumnsToContents()
        except Exception as e:
            print(f"Ошибка при обновлении таблицы: {e}")

    def showEvent(self, event):
        self.load_data()
        super().showEvent(event)


class ClientsWindow(QWidget):
    def __init__(self, items_data, clients_data, save_data_func, parent=None):
        super().__init__(parent)
        self.items = items_data
        self.clients = clients_data
        self.save_data_func = save_data_func
        self.setWindowTitle("Клиенты")
        self.resize(900, 700)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        left_panel = QVBoxLayout()
        self.client_list = QListWidget()
        self.client_list.itemClicked.connect(self.show_client_info)
        left_panel.addWidget(QLabel("Список клиентов:"))
        left_panel.addWidget(self.client_list)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        left_panel.addLayout(btn_layout)

        main_layout.addLayout(left_panel)

        self.detail_group = QGroupBox("Информация о клиенте")
        detail_layout = QVBoxLayout()

        info_group = QGroupBox("Основная информация")
        info_layout = QFormLayout()

        self.name_label = QLabel()
        self.phone_label = QLabel()
        self.comment_label = QLabel()
        self.comment_edit = QTextEdit()
        self.comment_edit.setMaximumHeight(100)

        info_layout.addRow("Имя:", self.name_label)
        info_layout.addRow("Телефон:", self.phone_label)
        info_layout.addRow("Комментарий:", self.comment_edit)
        info_group.setLayout(info_layout)
        detail_layout.addWidget(info_group)

        items_group = QGroupBox("Назначенные позиции")
        items_layout = QVBoxLayout()

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(3)
        self.items_table.setHorizontalHeaderLabels(["Позиция", "Полка", "Количество"])
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)

        items_layout.addWidget(self.items_table)
        items_group.setLayout(items_layout)
        detail_layout.addWidget(items_group)

        items_btn_layout = QHBoxLayout()
        self.add_item_btn = QPushButton("Добавить позицию")
        self.remove_item_btn = QPushButton("Удалить позицию")
        items_btn_layout.addWidget(self.add_item_btn)
        items_btn_layout.addWidget(self.remove_item_btn)
        detail_layout.addLayout(items_btn_layout)

        self.detail_group.setLayout(detail_layout)
        main_layout.addWidget(self.detail_group)

        self.add_btn.clicked.connect(self.add_client)
        self.edit_btn.clicked.connect(self.edit_client)
        self.delete_btn.clicked.connect(self.delete_client)
        self.add_item_btn.clicked.connect(self.add_client_item)
        self.remove_item_btn.clicked.connect(self.remove_client_item)
        self.comment_edit.textChanged.connect(self.save_client_comment)

        self.refresh_client_list()

    def save_client_data(self):
        if callable(self.save_data_func):
            self.save_data_func()

    def save_client_comment(self):
        current = self.client_list.currentItem()
        if current:
            client = next(c for c in self.clients if c["name"] == current.text())
            client["comment"] = self.comment_edit.toPlainText()

    def refresh_client_list(self):
        self.client_list.clear()
        for client in self.clients:
            self.client_list.addItem(client["name"])

    def update_client_items_table(self, client):
        self.items_table.setRowCount(0)

        for item in client.get("items", []):
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)

            shelf_name = ""
            for shelf, items in self.items.items():
                if any(i['name'] == item['name'] for i in items):
                    shelf_name = shelf
                    break

            self.items_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.items_table.setItem(row, 1, QTableWidgetItem(shelf_name))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))

    def show_client_info(self, item):
        client_name = item.text()
        client = None

        for c in self.clients:
            if c["name"] == client_name:
                client = c
                break

        if not client:
            pass
            return

        self.name_label.setText(client['name'])
        self.phone_label.setText(client.get('phone', ''))
        self.comment_edit.setPlainText(client.get('comment', ''))

        self.update_client_items_table(client)

    def add_client(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить клиента")
        layout = QVBoxLayout(dialog)

        form = QFormLayout()
        name_edit = QLineEdit()
        phone_edit = QLineEdit()
        comment_edit = QTextEdit()
        comment_edit.setMaximumHeight(80)

        form.addRow("Имя:", name_edit)
        form.addRow("Телефон:", phone_edit)
        form.addRow("Комментарий:", comment_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            name = name_edit.text()
            phone = phone_edit.text()
            comment = comment_edit.toPlainText()

            if not name:
                QMessageBox.warning(self, "Ошибка", "Имя обязательно")
                return

            self.clients.append({
                "name": name,
                "phone": phone,
                "comment": comment,
                "items": []
            })
            self.refresh_client_list()
            self.save_client_data()

    def edit_client(self):
        current = self.client_list.currentItem()
        if not current:
            return

        client = next(c for c in self.clients if c["name"] == current.text())
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать клиента")
        layout = QVBoxLayout(dialog)

        form = QFormLayout()
        name_edit = QLineEdit(client["name"])
        phone_edit = QLineEdit(client.get("phone", ""))
        comment_edit = QTextEdit(client.get("comment", ""))
        comment_edit.setMaximumHeight(80)

        form.addRow("Имя:", name_edit)
        form.addRow("Телефон:", phone_edit)
        form.addRow("Комментарий:", comment_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            name = name_edit.text()
            phone = phone_edit.text()
            comment = comment_edit.toPlainText()

            if not name:
                QMessageBox.warning(self, "Ошибка", "Имя обязательно")
                return

            client["name"] = name
            client["phone"] = phone
            client["comment"] = comment
            self.refresh_client_list()
            self.show_client_info(current)
            self.save_client_data()

    def delete_client(self):
        current = self.client_list.currentItem()
        if not current:
            return

        client_name = current.text()

        client_index = -1
        for i, client in enumerate(self.clients):
            if client["name"] == client_name:
                client_index = i
                break

        if client_index == -1:
            QMessageBox.warning(self, "Ошибка", "Клиент не найден!")
            self.refresh_client_list()
            return

        reply = QMessageBox.question(
            self,
            "Удаление клиента",
            f"Вы уверены, что хотите удалить клиента {client_name}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            del self.clients[client_index]

            self.refresh_client_list()
            self.name_label.setText("")
            self.phone_label.setText("")
            self.comment_edit.setPlainText("")
            self.items_table.setRowCount(0)

            self.save_client_data()
            QMessageBox.information(self, "Успех", "Клиент удален!")


    def add_client_item(self):
        current = self.client_list.currentItem()
        if not current:
            return

        client = next(c for c in self.clients if c["name"] == current.text())

        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить позицию")
        layout = QVBoxLayout(dialog)

        shelf_combo = QComboBox()
        shelf_combo.addItems(sorted(self.items.keys()))

        item_combo = QComboBox()

        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, 9999)

        def update_items():
            shelf = shelf_combo.currentText()
            item_combo.clear()
            if shelf in self.items:
                item_combo.addItems([item["name"] for item in self.items[shelf]])

        shelf_combo.currentTextChanged.connect(update_items)
        update_items()

        form = QFormLayout()
        form.addRow("Полка:", shelf_combo)
        form.addRow("Позиция:", item_combo)
        form.addRow("Количество:", quantity_spin)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            shelf = shelf_combo.currentText()
            item_name = item_combo.currentText()
            quantity = quantity_spin.value()

            if any(item["name"] == item_name for item in client.get("items", [])):
                QMessageBox.warning(self, "Ошибка", "Эта позиция уже добавлена клиенту")
                return

            client.setdefault("items", []).append({
                "name": item_name,
                "quantity": quantity
            })

            self.show_client_info(current)
            self.save_client_data()

    def remove_client_item(self):
        current = self.client_list.currentItem()
        if not current:
            return

        selected = self.items_table.currentRow()
        if selected < 0:
            return

        client = next(c for c in self.clients if c["name"] == current.text())
        item_name = self.items_table.item(selected, 0).text()

        reply = QMessageBox.question(
            self,
            "Удаление позиции",
            f"Удалить позицию {item_name} у клиента {client['name']}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            client["items"] = [item for item in client["items"] if item["name"] != item_name]
            self.show_client_info(current)
            self.save_client_data()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mainWin = Ui_MainWindow()
    mainWin.show()
    sys.exit(app.exec_())