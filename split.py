import os
import shutil
import random

# Путь к исходным папкам
source_folders = ["dataset_raw/meal", "dataset_raw/drink", "dataset_raw/dessert"]

# Путь для сохранения результатов
output_folder = "./dataset"
train_folder = os.path.join(output_folder, "train")
val_folder = os.path.join(output_folder, "val")

# Создаем папки train и val
os.makedirs(train_folder, exist_ok=True)
os.makedirs(val_folder, exist_ok=True)


# Функция для разделения файлов
def split_files(folder, train_folder, val_folder, val_ratio=0.1):
    # Название класса (папки)
    class_name = os.path.basename(folder)

    # Папки для текущего класса
    train_class_folder = os.path.join(train_folder, class_name)
    val_class_folder = os.path.join(val_folder, class_name)

    # Создаем папки для текущего класса
    os.makedirs(train_class_folder, exist_ok=True)
    os.makedirs(val_class_folder, exist_ok=True)

    # Получаем список файлов
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    random.shuffle(files)  # Перемешиваем файлы

    # Делим на train и val
    val_count = int(len(files) * val_ratio)
    val_files = files[:val_count]
    train_files = files[val_count:]

    # Копируем файлы
    for file in train_files:
        shutil.copy(os.path.join(folder, file), os.path.join(train_class_folder, file))

    for file in val_files:
        shutil.copy(os.path.join(folder, file), os.path.join(val_class_folder, file))


# Обрабатываем каждую папку
for folder in source_folders:
    split_files(folder, train_folder, val_folder)

print("Файлы успешно разделены на train и val с сохранением структуры классов!")
