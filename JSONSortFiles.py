import os
import shutil
import sys


def rename_annotations(folder_path):
    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found: {folder_path}")
        return

    images = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(('.jpg', '.jpeg'))
    ]
    jsons = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith('.json')
    ]

    if not images:
        print("No image files (.jpg/.jpeg) found in the folder.")
        return

    print(f"Found {len(images)} images and {len(jsons)} JSON files.")

    file_times = {}
    for f in images + jsons:
        path = os.path.join(folder_path, f)
        if os.path.exists(path):
            file_times[f] = os.path.getmtime(path)

    images_sorted = sorted(images, key=lambda x: file_times.get(x, float('inf')))

    matched = {}
    remaining_jsons = jsons.copy()

    for img in images_sorted:
        img_time = file_times.get(img, float('inf'))
        if not remaining_jsons:
            break
        closest_json = min(
            remaining_jsons,
            key=lambda x: abs(file_times.get(x, float('inf')) - img_time)
        )
        matched[img] = closest_json
        remaining_jsons.remove(closest_json)

    for i, img in enumerate(images_sorted, start=1):
        base_name = f"image-{i}"

        img_ext = os.path.splitext(img)[1]
        new_img_name = base_name + img_ext
        old_img_path = os.path.join(folder_path, img)
        new_img_path = os.path.join(folder_path, new_img_name)

        os.rename(old_img_path, new_img_path)
        print(f"Renamed image: {img} → {new_img_name}")

        if img in matched:
            json_file = matched[img]
            new_json_name = base_name + '.json'
            old_json_path = os.path.join(folder_path, json_file)
            new_json_path = os.path.join(folder_path, new_json_name)

            os.rename(old_json_path, new_json_path)
            print(f"  → Renamed JSON: {json_file} → {new_json_name}")

    if remaining_jsons:
        print("\nUnmatched JSON files (no corresponding image):")
        unmatched_dir = os.path.join(folder_path, 'unmatched_json')
        os.makedirs(unmatched_dir, exist_ok=True)
        for json_file in remaining_jsons:
            old_path = os.path.join(folder_path, json_file)
            new_path = os.path.join(unmatched_dir, json_file)
            shutil.move(old_path, new_path)
            print(f"  Moved: {json_file} → unmatched_json/")

    print("\nRenaming complete!")
    print("Images renamed to image-1.jpg, image-2.jpg, etc.")
    print("Matched JSONs renamed to image-1.json, image-2.json, etc.")
    print(f"Check folder: {folder_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rename_annotations.py /path/to/your/folder")
        sys.exit(1)

    folder_path = sys.argv[1]
    rename_annotations(folder_path)