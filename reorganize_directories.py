import os
import shutil

def reorganize_directories(images_dir, embeddings_dir):
    for root, dirs, _ in os.walk(images_dir):
        for subdir in dirs:
            new_directory = os.path.join(os.path.dirname(images_dir), subdir)

            # 移动 images 子文件夹
            old_images_subdir = os.path.join(images_dir, subdir)
            new_images_subdir = os.path.join(new_directory, "images")
            os.makedirs(new_images_subdir, exist_ok=True)
            for item in os.listdir(old_images_subdir):
                shutil.move(os.path.join(old_images_subdir, item), os.path.join(new_images_subdir, item))

            # 移动 embeddings 子文件夹
            old_embeddings_subdir = os.path.join(embeddings_dir, subdir)
            new_embeddings_subdir = os.path.join(new_directory, "embeddings")
            os.makedirs(new_embeddings_subdir, exist_ok=True)
            for item in os.listdir(old_embeddings_subdir):
                shutil.move(os.path.join(old_embeddings_subdir, item), os.path.join(new_embeddings_subdir, item))

            # 删除原始子文件夹
            os.rmdir(old_images_subdir)
            os.rmdir(old_embeddings_subdir)

def main():
    images_dir = "../datasets/scrap/images"
    embeddings_dir = "../datasets/scrap/embeddings"

    reorganize_directories(images_dir, embeddings_dir)

if __name__ == "__main__":
    main()
