# Интерфейс + рекация на действия пользователя
import csv
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton,\
        QVBoxLayout, QWidget, QLabel, QHBoxLayout, QLineEdit, \
        QTableWidget, QTableWidgetItem, QComboBox, QMessageBox,  QFileDialog, QTabWidget

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from data_manager import DataManager
from dialogs import ShipDialog


# Цвета статусов
STATUS_COLORS = {
    "Свободна": QColor("#c8f7c5"),
    "Забронирована": QColor("#ffeaa7"),
    "Оплачена": QColor("#a8c8ff")
    }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dm = DataManager()
        self.setWindowTitle("Упаравление бронированием номеров")
        self.resize(1200, 700)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)  

        self.tabs.addTab(self._build_ships_tab(), "Корабли")
        self.tabs.addTab(self._build_cabins_tab(), "Каюты")
        self.tabs.addTab(self._build_bookings_tab(), "Бронирования")

    #  ------ корабли ------
    def _build_ships_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        # поиск
        search_row = QHBoxLayout()
        self.ships_search = QLineEdit()
        self.ships_search.setPlaceholderText("Поиск по названию корабля")
        self.ships_search.textChanged.connect(self._filter_ships)
        search_row.addWidget(self.ships_search)
        layout.addLayout(search_row)

        # таблица кораблей
        self.ships_table = QTableWidget()
        self.ships_table.setColumnCount(3)
        self.ships_table.setHorizontalHeaderLabels(["ID", "Название", "Тип"])
        self.ships_table.horizontalHeader().setStretchLastSection(True)
        self.ships_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.ships_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.ships_table.setAlternatingRowColors(True)
        layout.addWidget(self.ships_table)

        # кнопки
        btn_row = QHBoxLayout()
        btn_add = QPushButton("Добавить корабль")
        btn_edit = QPushButton("Редактировать")
        btn_delete = QPushButton("Удалить")
        btn_export = QPushButton("Экспорт в CSV")

        btn_add.clicked.connect(self._add_ship)
        btn_edit.clicked.connect(self._edit_ship)
        btn_delete.clicked.connect(self._delete_ship)
        btn_export.clicked.connect(lambda: self._export_to_csv(self.ships_table, "ships"))

        for btn in [btn_add, btn_edit, btn_delete, btn_export]:
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

        self._refresh_ships()
        return widget

    def _refresh_ships(self):
            ships = self.dm.get_ships()
            self._fill_ships_table(ships)

    def _fill_ships_table(self, ships):
        self.ships_table.setRowCount(0)
        for ship in ships:
            row = self.ships_table.rowCount()
            self.ships_table.insertRow(row)
            self.ships_table.setItem(row, 0, QTableWidgetItem(str(ship["id"])))
            self.ships_table.setItem(row, 1, QTableWidgetItem(ship["name"]))
            self.ships_table.setItem(row, 2, QTableWidgetItem(ship["type"]))
        self.ships_table.resizeColumnsToContents()

    def _filter_ships(self):
        query = self.ships_search.text().lower()
        filtered = [ship for ship in self.dm.get_ships() if query in ship["name"].lower()]
        self._fill_ships_table(filtered)

    def _get_selected_ship_id(self):
        row = self.ships_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите корабль в таблице.")
            return None
        return int(self.ships_table.item(row, 0).text())

    def _add_ship(self):
        dlg = ShipDialog(self)
        if dlg.exec() == ShipDialog.DialogCode.Accepted:
            d = dlg.get_data()
            self.dm.add_ship(d["name"], d["type"])
            self._refresh_ships()
            self._refresh_cabins()


    def _edit_ship(self):
        ship_id = self._get_selected_ship_id()
        if ship_id is None:
            return
        ship = next((s for s in self.dm.get_ships() if s["id"] == ship_id), None)
        if not ship:
            return

        dlg = ShipDialog(self, ship=ship)
        if dlg.exec() == ShipDialog.DialogCode.Accepted:
            d = dlg.get_data()
            self.dm.update_ship(ship_id, d["name"], d["type"])
            self._refresh_ships()
            self._refresh_cabins()
            self._refresh_bookings()

    def _delete_ship(self):
        ship_id = self._get_selected_ship_id()
        if ship_id is None:
            return

        ship_name = self.dm.get_ship_name(ship_id)

        ans = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить корабль «{ship_name}»?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if ans == QMessageBox.StandardButton.Yes:
            self.dm.delete_ship(ship_id)
            self._refresh_ships()

    def _export_to_csv(self, table, name):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить CSV", f"{name}.csv", "CSV файлы (*.csv)"
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")

                # Заголовки таблицы
                headers = [
                    table.horizontalHeaderItem(c).text()
                    for c in range(table.columnCount())
                ]
                writer.writerow(headers)

                # Данные строк
                for row in range(table.rowCount()):
                    row_data = [
                        table.item(row, col).text() if table.item(row, col) else ""
                        for col in range(table.columnCount())
                    ]
                    writer.writerow(row_data)

            QMessageBox.information(self, "Готово", f"Файл успешно сохранён:\n{path}")
        except IOError as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")

    # --- каюты ---
    def _build_cabins_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Строка поиска и фильтр по статусу
        filter_row = QHBoxLayout()
        self.cabins_search = QLineEdit()
        self.cabins_search.setPlaceholderText(" Поиск по номеру, классу, кораблю...")
        self.cabins_search.textChanged.connect(self._filter_cabins)

        self.cabins_status_filter = QComboBox()
        self.cabins_status_filter.addItems(["Все", "Свободна", "Забронирована", "Оплачена"])
        self.cabins_status_filter.currentTextChanged.connect(self._filter_cabins)

        filter_row.addWidget(self.cabins_search, 3)
        filter_row.addWidget(QLabel("Статус:"))
        filter_row.addWidget(self.cabins_status_filter, 1)
        layout.addLayout(filter_row)

        # Таблица кают
        self.cabins_table = QTableWidget()
        self.cabins_table.setColumnCount(6)
        self.cabins_table.setHorizontalHeaderLabels(
            ["ID", "Корабль", "Номер", "Класс", "Вместимость", "Статус"]
        )
        self.cabins_table.horizontalHeader().setStretchLastSection(True)
        self.cabins_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.cabins_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cabins_table.setAlternatingRowColors(True)
        layout.addWidget(self.cabins_table)

        # Кнопки действий
        btn_row = QHBoxLayout()
        btn_add = QPushButton("Добавить каюту")
        btn_edit = QPushButton("Редактировать")
        btn_del = QPushButton("Удалить")
        btn_status = QPushButton("Изменить статус")

        # Привязка кнопок (раскоментировать по мере создания методов)
        # btn_add.clicked.connect(self._add_cabin)
        # btn_edit.clicked.connect(self._edit_cabin)
        # btn_del.clicked.connect(self._delete_cabin)
        # btn_status.clicked.connect(self._change_cabin_status)

        for btn in (btn_add, btn_edit, btn_del, btn_status):
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

        self._refresh_cabins()
        return widget

    def _filter_cabins(self):
        pass

    def _refresh_cabins(self): # исправил slef -> self
        pass



    # -- бронирования --
    def _build_bookings_tab(self):
        pass

    def _refresh_bookings(self):
        pass

    