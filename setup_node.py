import urllib.request
import zipfile
import os
import sys

NODE_URL = "https://nodejs.org/dist/v20.18.0/node-v20.18.0-win-x64.zip"
TARGET_DIR = os.path.join(os.getcwd(), "tools", "node")
ZIP_FILE = os.path.join(os.getcwd(), "tools", "node.zip")

os.makedirs(os.path.join(os.getcwd(), "tools"), exist_ok=True)

if not os.path.exists(os.path.join(TARGET_DIR, "node.exe")):
    print(f"Downloading Node.js portable from {NODE_URL}...")
    urllib.request.urlretrieve(NODE_URL, ZIP_FILE)
    print("Extracting Node.js...")
    with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
        zip_ref.extractall(os.path.join(os.getcwd(), "tools"))
    
    extracted_folder = os.path.join(os.getcwd(), "tools", "node-v20.18.0-win-x64")
    if os.path.exists(extracted_folder):
        if os.path.exists(TARGET_DIR):
            import shutil
            shutil.rmtree(TARGET_DIR)
        os.rename(extracted_folder, TARGET_DIR)
    if os.path.exists(ZIP_FILE):
        os.remove(ZIP_FILE)
    print("Node.js portable setup successfully!")
else:
    print("Node.js already present at:", TARGET_DIR)

