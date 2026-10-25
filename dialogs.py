# окна для ввода данных пользователем
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QPushButton, QMessageBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt

from datetime import date

class ShipDialog(QDialog):
    def __init__(self, parent=None, ship=None):
        super().__init__(parent)
        self.ship = ship
        self.setWindowTitle("Редактировать корабль" if ship else "Добавить корабль")
        self.setMinimumWidth(380)
        self._build_ui()
        if ship:
            self._fill_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите название корабля")

        self.type_edit = QLineEdit()
        self.type_edit.setPlaceholderText("Введите тип корабля: Пассажирский / Круизный / Грузовой")

        form.addRow("Название:", self.name_edit)
        form.addRow("Тип:", self.type_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _fill_data(self):
        self.name_edit.setText(self.ship["name"])
        self.type_edit.setText(self.ship["type"])

    def _validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название корабля.")
            return
        if not self.type_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите тип корабля.")
            return  
        self.accept()


    def get_data(self):
        return {
            "name": self.name_edit.text().strip(),
            "type": self.type_edit.text().strip(),
        }

class CabinDialog(QDialog):
    def __init__(self, parent=None, cabin=None, ships=None):
        super().__init__(parent)
        self.cabin = cabin
        self.ships = ships or []
        self.setWindowTitle("Редактировать каюту" if cabin else "Добавить каюту")
        self.setMinimumWidth(380)
        self._build_ui()
        if cabin:
            self._fill_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.ship_combo = QComboBox()
        for ship in self.ships:
            self.ship_combo.addItem(ship["name"], ship["id"])

        self.number_edit = QLineEdit()
        self.number_edit.setPlaceholderText("Например: A101")

        self.class_edit = QLineEdit()
        self.class_edit.setPlaceholderText("Люкс / Стандарт / Семейная")

        self.capacity_spin = QSpinBox()
        self.capacity_spin.setRange(1, 50)
        self.capacity_spin.setValue(2)

        form.addRow("Корабль:", self.ship_combo)
        form.addRow("Номер каюты:", self.number_edit)
        form.addRow("Класс:", self.class_edit)
        form.addRow("Вместимость:", self.capacity_spin)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.standardButton.Ok | QDialogButtonBox.standardButton.Cancel
        )

        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate_and_accept(self):
        if not self.number_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите номер каюты.")
            return
        if not self.class_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите класс каюты.")
            return
        self.accept()

    def get_data(self):
        return {
            "ship_id": self.ship_combo.currentData(),
            "cabin_number": self.number_edit.text().strip(),
            "class_type": self.class_edit.text().strip(),
            "capacity": self.capacity_spin.value()
        }

class BookingDialog(QDialog):
    """Диалог добавления / редактирования бронирования."""
    def __init__(self, parent=None, booking=None, cabin_id=None, cabin_number=None, dm=None):
        super().__init__(parent)
        self.booking = booking
        self.preset_cabin_id = cabin_id
        self.dm = dm
        self.setWindowTitle("Редактировать бронирование" if booking else "Забронировать каюту")
        self.setMinimumWidth(420)
        self._build_ui(cabin_number)

    def _build_ui(self, cabin_number=None):
        layout = QVBoxLayout()
        form = QFormLayout()

        # Выбор каюты (если не передан preset)
        self.cabin_combo = QComboBox()
        if self.dm:
            for cabin in self.dm.get_cabins():
                label = f"{cabin['cabin_number']} ({self.dm.get_ship_name(cabin['ship_id'])})"
                self.cabin_combo.addItem(label, cabin["id"])
                if self.preset_cabin_id and cabin["id"] == self.preset_cabin_id:
                    self.cabin_combo.setCurrentIndex(self.cabin_combo.count() - 1)

        if cabin_number:
            self.cabin_combo.setEnabled(False)

        self.guest_edit = QLineEdit()
        self.guest_edit.setPlaceholderText("ФИО гостя")

        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("ГГГГ-ММ-ДД")
        self.date_edit.setText(str(date.today()))


        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 9_999_999)
        self.price_spin.setDecimals(2)
        self.price_spin.setSuffix(" U+20BD") # U+20BD - ₽
        self.price_spin.setValue(5000)

        form.addRow("Каюта:", self.cabin_combo)
        form.addRow("Имя гостя:", self.guest_edit)
        form.addRow("Дата брони:", self.date_edit)
        form.addRow("Стоимость:", self.price_spin)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
                    QDialogButtonBox.standardButton.Ok | QDialogButtonBox.standardButton.Cancel
                )
        
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _fill_data(self):
        # Выбираем нужную каюту
        for i in range(self.cabin_combo.count()):
            if self.cabin_combo.itemData(i) == self.booking["cabin_id"]:
                self.cabin_combo.setCurrentIndex(i)
                break

        self.guest_edit.setText(self.booking["guest_name"])
        self.date_edit.setText(self.booking["booking_date"])
        self.price_spin.setText(self.booking["total_price"])

    def _validate_and_accept(self):
        if not self.guest_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите имя гостя.")
            return
        date_str = self.date_edit.text().strip()
        try:
            date.fromisoformat(date_str)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД.")
            return
        self.accept()

    def get_data(self):
        return {
            "cabin_id": self.cabin_combo.currentData(),
            "guest_name": self.guest_edit.text().strip(),
            "booking_date": self.date_edit.text().strip(),
            "total_price": self.price_spin.value()
        }


class StatusDialog(QDialog):
    """Диалог изменения статуса каюты."""
 
    def __init__(self, parent=None, current_status="Свободна"):
        super().__init__(parent)
        self.setWindowTitle("Изменить статус каюты")
        self.setMinimumWidth(300)
 
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Выберите новый статус:"))
 
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Свободна", "Забронирована", "Оплачена"])
        self.status_combo.setCurrentText(current_status)
        layout.addWidget(self.status_combo)
 
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
 
    def get_status(self):
        return self.status_combo.currentText()