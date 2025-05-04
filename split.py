import os
import shutil
import random

raw_dataset_path = "dataset2_raw"
output_folder = "./dataset"
train_folder = os.path.join(output_folder, "train")
val_folder = os.path.join(output_folder, "val")

val_ratio = 0.1

os.makedirs(train_folder, exist_ok=True)
os.makedirs(val_folder, exist_ok=True)

source_folders = []
for parent in os.listdir(raw_dataset_path):
    parent_path = os.path.join(raw_dataset_path, parent)
    if not os.path.isdir(parent_path):
        continue
    for child in os.listdir(parent_path):
        child_path = os.path.join(parent_path, child)
        if os.path.isdir(child_path):
            source_folders.append(child_path)


def split_and_copy(folder_path, val_ratio):
    class_name = os.path.basename(folder_path)

    train_dest = os.path.join(train_folder, class_name)
    val_dest = os.path.join(val_folder, class_name)
    os.makedirs(train_dest, exist_ok=True)
    os.makedirs(val_dest, exist_ok=True)

    files = [f for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]
    random.shuffle(files)

    n_val = int(len(files) * val_ratio)
    val_files = files[:n_val]
    train_files = files[n_val:]

    # копируем
    for fname in train_files:
        shutil.copy(
            os.path.join(folder_path, fname),
            os.path.join(train_dest, fname)
        )
    for fname in val_files:
        shutil.copy(
            os.path.join(folder_path, fname),
            os.path.join(val_dest, fname)
        )


for folder in source_folders:
    split_and_copy(folder, val_ratio)

print("Готово! Копируются и сплитятся только подпапки второго уровня.")
