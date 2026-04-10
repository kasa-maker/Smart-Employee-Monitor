from deepface import DeepFace
import inspect

print("=== Available DeepFace Models ===\n")

# Try to get the represent function signature
sig = inspect.signature(DeepFace.represent)
print("represent() parameters:")
print(sig)
print("\n")

# Try to list models
try:
    print("DeepFace.modelNames:", DeepFace.modelNames)
except:
    print("modelNames not available")

# Try to represent with a simple model
print("\nTrying different models...")
models_to_try = ["Facenet512", "ArcFace", "Dlib", "SFace"]
for model in models_to_try:
    print(f"  - {model}")
