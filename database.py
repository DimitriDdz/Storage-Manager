import json
import os
from datetime import datetime

DATA_FILE = "storage_data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return [], {}, [], []  # Добавлен пустой список для clients
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Добавлены значения по умолчанию для всех полей
    return (
        data.get("shelves", []),
        data.get("items", {}),
        data.get("archive", []),
        data.get("clients", [])
    )

def save_data(shelves, items, archive, clients):
    data = {
        "shelves": shelves,
        "items": items,
        "archive": archive,
        "clients": clients
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def delete_image(path):
    if os.path.exists(path):
        os.remove(path)


def save_image(image_path):
    if not image_path:
        return ""

    # Создаем папку для изображений, если ее нет
    os.makedirs("item_images", exist_ok=True)

    # Генерируем уникальное имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"item_images/{timestamp}_{os.path.basename(image_path)}"

    # Копируем файл
    import shutil
    shutil.copy(image_path, filename)

    return filename