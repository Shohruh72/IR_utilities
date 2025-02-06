import os
import cv2
import random
import shutil
from PIL import Image
from collections import Counter


def get_sub_imgs(path, target_path):
    extensions = ['.xml', '.jpeg', '.png', '.gif', '.bmp', '.tiff']

    os.makedirs(target_path, exist_ok=True)
    for dirs, _, files in os.walk(path):
        if dirs != path:
            for filename in files:
                if any(filename.lower().endswith(ext) for ext in extensions):
                    source = os.path.join(dirs, filename)

                    target = os.path.join(target_path, filename)
                    base, ext = os.path.splitext(target)
                    counter = 1
                    while os.path.exists(target):
                        target = f"{base}_{counter}{ext}"
                        counter += 1

                    shutil.move(source, target)


def verify_name_pairs(image_path, label_path):
    # List directory contents
    images = os.listdir(image_path)
    labels = os.listdir(label_path)

    # Supported image formats
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')

    # Extract filenames without extensions and filter based on desired extensions
    image_names = [os.path.splitext(im)[0] for im in images if im.endswith(image_extensions)]
    label_names = [os.path.splitext(lab)[0] for lab in labels if
                   lab.endswith('.txt')]

    # Find unmatched image and label names
    diff_img_label = list((Counter(image_names) - Counter(label_names)).elements())
    diff_label_img = list((Counter(label_names) - Counter(image_names)).elements())

    # Report any mismatches
    if diff_img_label or diff_label_img or len(images) != len(labels):
        print("Error comes from images folder:", diff_img_label)
        print("Error comes from label folder:", diff_label_img)
        print('Please check folders.')
    else:
        print('OK...')


def visualize_landmarks(image_name, pts_name, output_name=None):
    with open(pts_name, 'r') as file:
        content = file.readlines()

    start_idx = next(i for i, line in enumerate(content) if "{" in line) + 1
    end_idx = next(i for i, line in enumerate(content) if "}" in line)
    landmarks_data = content[3:-3]

    landmarks = [tuple(map(float, line.split())) for line in landmarks_data]

    img = cv2.imread(image_name)

    for idx, (x, y) in enumerate(landmarks):
        cv2.circle(img, (int(x), int(y)), 2, (0, 0, 255), -1)  # Drawing a red circle for each point
        cv2.putText(img, str(idx+1), (int(x) + 2, int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

    cv2.imshow("Face Landmarks", img)

    if output_name:
        cv2.imwrite(output_name, img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()



def split_dataset(main_folder, train_folder, test_folder, test_ratio=0.2):
    image_extensions = ['.png']
    label_extensions = ['.pts']
    # Ensure the train and test folders exist
    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(test_folder, exist_ok=True)

    # Get all image files from the main folder
    image_files = [f for f in os.listdir(main_folder) if os.path.isfile(os.path.join(main_folder, f)) and any(
        f.lower().endswith(ext) for ext in image_extensions)]

    # Shuffle and split the files
    random.shuffle(image_files)
    split_index = int(len(image_files) * (1 - test_ratio))
    train_files = image_files[:split_index]
    test_files = image_files[split_index:]

    # Move files function (nested within the main function)
    def move_files(files, source_folder, destination_folder):
        for filename in files:
            # Move the image file
            shutil.move(os.path.join(source_folder, filename), os.path.join(destination_folder, filename))

            # Move the corresponding label file
            base_name, _ = os.path.splitext(filename)
            for ext in label_extensions:
                label_file = f"{base_name}{ext}"
                label_path = os.path.join(source_folder, label_file)
                if os.path.exists(label_path):
                    shutil.move(label_path, os.path.join(destination_folder, label_file))

    # Call the move files function for train and test data
    move_files(train_files, main_folder, train_folder)
    move_files(test_files, main_folder, test_folder)


def collect_files(src1, src2, destination):
    os.makedirs(destination, exist_ok=True)

    def copy_from_source(src):
        for filename in os.listdir(src):
            file_path = os.path.join(src, filename)
            if os.path.isfile(file_path):
                shutil.copy(file_path, os.path.join(destination, filename))

    copy_from_source(src1)
    copy_from_source(src2)


def convert_PNG(folder_path):
    supported_formats = ("jpeg", "jpg", 'JPG', 'JPEG')

    converted_and_removed_count = 0
    i = 0
    for root, _, files in os.walk(folder_path):
        for file in files:
            i += 1
            if file.lower().endswith(supported_formats):
                try:
                    file_path = os.path.join(root, file)

                    img = Image.open(file_path)

                    new_file_path = os.path.splitext(file_path)[0] + ".png"

                    img.save(new_file_path, "PNG")

                    os.remove(file_path)

                    converted_and_removed_count += 1

                    print(f"Converted and removed: {file_path} -> {new_file_path}")
                except Exception as e:
                    print(f"Failed to convert and remove {file}: {e}")
            print('i = ', i)
    print(f"Total images converted and removed: {converted_and_removed_count}")


def move_different_files(images_folder, labels_folder, different_folder):
    if not os.path.exists(different_folder):
        os.makedirs(different_folder)

    image_files = set(os.listdir(images_folder))
    label_files = set(os.listdir(labels_folder))

    image_names = {os.path.splitext(file)[0] for file in image_files}
    label_names = {os.path.splitext(file)[0] for file in label_files}

    different_images = image_names - label_names
    different_files = [file for file in image_files if os.path.splitext(file)[0] in different_images]

    for file in different_files:
        src = os.path.join(images_folder, file)
        dest = os.path.join(different_folder, file)
        shutil.move(src, dest)
        print(f"Moved: {file}")


def rename_files(directory):
    for foldername in os.listdir(directory):
        folder_path = os.path.join(directory, foldername)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                old_file_path = os.path.join(folder_path, filename)
                new_filename = filename.replace(' ', '')
                new_file_path = os.path.join(folder_path, new_filename)

                if old_file_path != new_file_path:
                    os.rename(old_file_path, new_file_path)
                    print(f"Renamed: {old_file_path} -> {new_file_path}")
