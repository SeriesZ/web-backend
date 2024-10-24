import os

ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DOWNLOAD_DIR = os.path.join(ROOT_PATH, 'temporary/downloads')
ASSETS_DIR = os.path.join(ROOT_PATH, 'temporary/assets')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
