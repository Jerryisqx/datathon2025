import os
import zipfile

def extract_zip(zip_path, extract_to):
    """Extract a zip file to a specified directory"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def find_all_zip_files(root_dir):
    """Recursively find all zip files in a given directory"""
    zip_paths = []
    for foldername, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.zip'):
                full_path = os.path.join(foldername, filename)
                zip_paths.append(full_path)
    return zip_paths

def recursive_unzip_all(start_dir='.'):
    extracted = set()

    while True:
        zip_files = find_all_zip_files(start_dir)
        new_zip_files = [z for z in zip_files if z not in extracted]

        if not new_zip_files:
            break

        for zip_file in new_zip_files:
            target_dir = os.path.splitext(zip_file)[0] 
            print(f"Unzip: {zip_file} -> {target_dir}")
            os.makedirs(target_dir, exist_ok=True)
            try:
                extract_zip(zip_file, target_dir)
                extracted.add(zip_file)
            except Exception as e:
                print(f"⚠️ Unzip failed{zip_file}, : Error{e}")


if __name__ == "__main__":
    recursive_unzip_all()
