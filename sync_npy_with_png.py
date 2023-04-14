import os
import shutil

def get_file_list(base_path, file_ext):
    file_list = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(file_ext):
                file_list.append(os.path.splitext(file)[0])
    return file_list

def main():
    images_dir = "../datasets/scrap/images"
    embeddings_dir = "../datasets/scrap/embeddings"

    png_files = get_file_list(images_dir, ".png")
    npy_files = get_file_list(embeddings_dir, ".npy")

    # 删除所有没有对应png格式文件名称的npy格式文件
    for npy_file in npy_files:
        if npy_file not in png_files:
            os.remove(os.path.join(embeddings_dir, f"{npy_file}.npy"))

    # 创建与images子文件夹相对应的子文件夹并将对应的npy文件移动到新子文件夹中
    for root, dirs, files in os.walk(images_dir):
        for subdir in dirs:
            new_subdir = os.path.join(embeddings_dir, subdir)
            os.makedirs(new_subdir, exist_ok=True)

            for npy_file in npy_files:
                npy_path = os.path.join(embeddings_dir, f"{npy_file}.npy")
                if os.path.exists(npy_path) and npy_file in png_files:
                    shutil.move(npy_path, os.path.join(new_subdir, f"{npy_file}.npy"))

if __name__ == "__main__":
    main()