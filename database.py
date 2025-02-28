import json
import os
import shutil

DATABASE_FILE = "storage_db.json"
IMAGES_FOLDER = "images"

def save_data(shelves, items):
    data = {
        "shelves": shelves,
        "items": items
    }
    with open(DATABASE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def load_data():
    if not os.path.exists(DATABASE_FILE):
        return [], {}

    with open(DATABASE_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data.get("shelves", []), data.get("items", {})

def save_image(image_path):
    if not image_path:
        return None

    if not os.path.exists(IMAGES_FOLDER):
        os.makedirs(IMAGES_FOLDER)

    filename = os.path.basename(image_path)
    destination = os.path.join(IMAGES_FOLDER, filename)
    shutil.copy(image_path, destination)
    return destination

def delete_image(image_path):
    if image_path and os.path.exists(image_path):
        os.remove(image_path)