import os
import shutil

source_dir = r"c:\Users\HP\Downloads\MSc-LLM-Remediation-Experiment"
dest_dir = r"c:\Users\HP\Downloads\llm-remediation-thesis-final\experiment\raw_outputs"

files_to_copy = [
    "package-lock.json",
    "juice_shop_package-lock.json"
]

for file in files_to_copy:
    src_path = os.path.join(source_dir, file)
    dest_path = os.path.join(dest_dir, file)
    if os.path.exists(src_path):
        print(f"Copying {file} to {dest_dir}...")
        shutil.copy2(src_path, dest_path)
    else:
        print(f"Warning: {src_path} not found.")

print("Copy operation completed.")
