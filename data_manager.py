# Бизне логика
import json
import os
from datetime import date

DATA_FILE = "data.json"

SEED_DATA = {
    "ships": [
        {"id": 1, "name": "Titanic", "type": "Пассажирский"},
        {"id": 2, "name": "Астория", "type": "Круизный"},
        # ...
    ],
    "сabins": [
        {"id": 1, "ship_id": 1, "cabin_number": "A101", "class_type": "Люкс", "capacity": 2, "status": "Свободна"},
        {"id": 2, "ship_id": 1, "cabin_number": "A102", "class_type": "Стандарт", "capacity": 4, "status": "Опалчен"},
        # ... статусы (Люкс, Стандарт, Семейный, Эконом), статутс (Свободна, Опалчен, Забронирована)
    ],
    "bookings": [
        {"id": 1, "cabin_id": 1, "guest_name": "Иван Иванов", "booking_date": "2026-06-01", "total_price": 15000.0},
        {"id": 2, "cabin_id": 2, "guest_name": "Иван Петров", "booking_date": "2026-06-02", "total_price": 20000.0}
        #...
    ],
}

class DataManager:
    def __init__(self):
        self.data = {}
        self.load_data()

    def load_data(self):
        '''Загрузка данных из  JSON файла'''
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                
                # Проверяем струтуру данных
                for key in ("ships", "cabins", "bookings"):
                    if key not in self.data:
                        self.data[key] = []
            else:
                self.data = SEED_DATA
                self.save_data()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка загрузки данных: {e}")
            self.data = SEED_DATA
            self.save_data()
            
    def save_data(self):
        '''Сохранение данных в JSON файл'''
        try:
            with open(DATA_FILE, "w", encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Ошибка сохранения данных: {e}")
        
    def get_next_id(self, collection_name):
        '''Полученние следующего ID для коллекции'''
        collection = self.data.get(collection_name, [])
        if not collection:
            return 1
        return max(item["id"] for item in collection) + 1 # получаем максимальный ID и прибавляем 1
        # прочитать про max() и list comprehension в Python

    
    # ---------- корабли ----------------------------------------------------------------------

    def get_ships(self):
        '''Получение списка кораблей'''
        return self.data.get("ships", [])

    def get_ship_name(self, ship_id):
        '''Получение имени корабля по ID'''
        for ship in self.data["ships"]:
            if ship["id"] == ship_id:
                return ship["name"]
        return "Неизвестно"
    
    def add_ship(self, name, ship_type):
        '''Добавление нового корабля'''
        ship = {
            "id": self.get_next_id("ships"),
            "name": name,
            "type": ship_type,
        }
        self.data["ships"].append(ship)
        self.save_data()

    def update_ship(self, ship_id, name, ship_type):
        '''Обновление информации о корабле'''
        # обновление информации о корабле по ID и сохранение данных
        print(f"Обновление корабля с ID {ship_id}: name={name}, type={ship_type}")
        for ship in self.data["ships"]:
            if ship["id"] == ship_id:
                ship["name"] = name
                ship["type"] = ship_type
                self.save_data()
                print(f"Корабль с ID {ship_id} обновлен.")

    def delete_ship(self, ship_id: int) -> bool:
        """Удаление корабля. Блокируется, если у него есть привязанные каюты."""
        if self.get_cabins_by_ship(ship_id):
            return False
        self.data["ships"] = [s for s in self.data["ships"] if s["id"] != ship_id]
        self.save_data()
        return True

    # ---------- каюты ----------------------------------------------------------------------

    def get_cabins(self):
        """Получение списка кают"""
        # TODO: Верни список кают по ключу "cabins" из словаря self.data.
        # Подсказка: используй метод .get("cabins", []), чтобы избежать ошибки, если ключа нет.
        return self.data.get("cabins", [])

    
    def get_cabins_by_ship(self, ship_id):
        """Получение списка кают по ID корабля"""
        # TODO: Сформируй и верни отфильтрованный список кают.
        # Каюта подходит, если значение её ключа 'ship_id' совпадает с переданным ship_id.
        # Подсказка: используй генератор списка (list comprehension) по self.get_cabins().
        return [c for c in self.get_cabins() if c["ship_id"] == ship_id]

    def get_cabin_by_id(self, cabin_id):
        """Получение каюты по ID"""
        # TODO 1: Пройди циклом for по всем каютам из self.get_cabins().
        # TODO 2: Если поле 'id' каюты совпадает с аргументом cabin_id — верни найденный словарь.
        # TODO 3: Если цикл завершился и каюта не найдена — верни None.
        for cabin in self.get_cabins():
            if cabin["id"] == cabin_id:
                return cabin
        return None
        

    def add_cabin(self, ship_id, cabin_number, class_type, capacity):
        """Добавление новой каюты"""
        cabin = {
            "id": self.get_next_id("cabins"),
            "ship_id": ship_id,
            "cabin_number": cabin_number,
            "class_type": class_type,
            "capacity": capacity,
            "status": "Свободна"
        }
        self.data["cabins"].append(cabin)
        self.save_data()
        return cabin

    def update_cabin(self, cabin_id, ship_id,  cabin_number, class_type, capacity):
        "Обновление информации о каюте"
        for cabin in self.data["cabins"]:
            if cabin["id"] == cabin_id:
                cabin["ship_id"] = ship_id
                cabin["cabin_number"] = cabin_number
                cabin["class_type"] = class_type
                cabin["capacity"] = capacity
                self.save_data()
                return True
        return False
    
    def update_cabin_status(self, cabin_id, status):
        for cabin in self.data["cabins"]:
            if cabin["id"] == cabin_id:
                cabin["status"] = status
                self.save_data()
                return True
        return False

    def delete_cabin(self, cabin_id):
        # Удаление кабины. Если есть бронь - удалять ее тоже
        self.data["bookings"] = [
            b for b in self.data["bookings"] if b["cabin_id"] != cabin_id
        ]
        self.data["cabins"] = [
            c for c in self.data["cabins"] if c["id"] != cabin_id
        ]
        self.save_data()

    # ---------- Бронирования ----------------------------------------------------------------------

    def get_bookings(self):
        "Получение списка бронирований"
        return self.data.get("bookings", [])

    def get_cabin_bookings(self, cabin_id):
        """Возвращает список бронирований для конкретной каюты."""
        return [b for b in self.get_bookings() if b["cabin_id"] == cabin_id]

    def get_booking_by_id(self, booking_id):
        for b in self.get_bookings():
            if b["id"] == booking_id:
                return b
        return None

    def add_booking(self, cabin_id, guest_name, booking_date, total_price):
        booking = {
            "id": self.get_next_id("bookings"),
            "cabin_id": cabin_id,
            "guest_name": guest_name,
            "booking_date": booking_date,
            "total_price": total_price
        }
        self.data["bookings"].append(booking)
        self.update_cabin_status(cabin_id, "Забронирована")
        self.save_data()
        return booking

    def update_booking(self, booking_id, guest_name, booking_date, total_price):
        for b in self.data["bookings"]:
            if b["id"] == booking_id:
                b["guest_name"] = guest_name
                b["booking_date"] = booking_date
                b["total_price"] = total_price
                self.save_data()
                return True
        return False

    def delete_booking(self, booking_id):
        """Удаление бронирования и сброс статуса каюты на 'Свободна'."""
        for booking in self.data["bookings"]:
            if booking["id"] == booking_id:
                cabin_id = booking["cabin_id"]
                self.data["bookings"].remove(booking)
                # Сброс статуса каюты на 'Свободна'
                for cabin in self.data["cabins"]:
                    if cabin["id"] == cabin_id:
                        cabin["status"] = "Свободна"
                        break
                self.save_data()


    
    def delete_booking_by_cabin(self, cabin_id):
        """Удаление бронирования по ID каюты (без сброса статуса)."""

        for booking in self.data["bookings"]:
            if booking["cabin_id"] == cabin_id:
                self.data["bookings"].remove(booking)
                self.save_data()
    




dm = DataManager()
dm.load_data()
print(dm.get_ships())