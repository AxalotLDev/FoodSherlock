import os
import shutil
import random

raw_dataset_path = "dataset_raw"

output_folder = "./dataset"
train_folder = os.path.join(output_folder, "train")
val_folder = os.path.join(output_folder, "val")

os.makedirs(train_folder, exist_ok=True)
os.makedirs(val_folder, exist_ok=True)

source_folders = [
    os.path.join(raw_dataset_path, folder)
    for folder in os.listdir(raw_dataset_path)
    if os.path.isdir(os.path.join(raw_dataset_path, folder))
]

def split_files(folder, train_folder, val_folder, val_ratio=0.1):
    class_name = os.path.basename(folder)
    train_class_folder = os.path.join(train_folder, class_name)
    val_class_folder = os.path.join(val_folder, class_name)
    os.makedirs(train_class_folder, exist_ok=True)
    os.makedirs(val_class_folder, exist_ok=True)
    files = [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ]
    random.shuffle(files)
    val_count = int(len(files) * val_ratio)
    val_files = files[:val_count]
    train_files = files[val_count:]

    for file in train_files:
        shutil.copy(os.path.join(folder, file), os.path.join(train_class_folder, file))
    for file in val_files:
        shutil.copy(os.path.join(folder, file), os.path.join(val_class_folder, file))


for folder in source_folders:
    split_files(folder, train_folder, val_folder)

print("Файлы успешно разделены на train и val с сохранением структуры классов!")
