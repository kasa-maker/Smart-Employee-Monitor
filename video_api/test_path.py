# test_path.py
import os

KNOWN_FACES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "known_faces")

print(f"Path: {KNOWN_FACES_DIR}")
print(f"Exists: {os.path.exists(KNOWN_FACES_DIR)}")
print(f"Files: {os.listdir(KNOWN_FACES_DIR)}")
