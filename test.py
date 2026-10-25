data = {
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
        {"id": 1, "cabin_id": 1, "guest_name": "Иван Иванов", "booking_data": "2026-06-01", "total_price": 15000.0},
        {"id": 2, "cabin_id": 2, "guest_name": "Иван Петров", "booking_data": "2026-06-02", "total_price": 20000.0}
        #...
    ],
}


ship_id = 2

for ship in data["ships"]:
    if ship["id"] == ship_id:
        data["ships"].remove(ship)
        print(f"Корабль с ID {ship_id} удален.")

print(data["ships"])