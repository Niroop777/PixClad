

# from ultralytics import YOLO
# import os
# from PIL import Image # <-- Import the Pillow library

# MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'yolo11n.pt')

# try:
#     model = YOLO(MODEL_PATH)
#     print("YOLO model loaded successfully.")
# except Exception as e:
#     print(f"FATAL: Could not load YOLO model. Error: {e}")
#     model = None

# def get_image_tags(image_path):
#     if model is None:
#         return ["Error: Model not loaded"]

#     try:
#         # --- FIX IS HERE: Clean the image before processing ---
#         # 1. Open the image with Pillow
#         img = Image.open(image_path)
#         # 2. Convert to a standard RGB format and save over the original
#         img.convert('RGB').save(image_path, 'jpeg')

#         # Now, process the cleaned image
#         results = model(image_path)

#         names = model.names
#         detected_classes = set()
#         for r in results:
#             for c in r.boxes.cls:
#                 detected_classes.add(names[int(c)])

#         if not detected_classes:
#             return ["Uncategorized"]

#         return list(detected_classes)
#     except Exception as e:
#         print(f"Error processing image with YOLO model: {e}")
#         return ["Error"]


from ultralytics import YOLO
import os
from PIL import Image

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'yolo11n.pt')

try:
    model = YOLO(MODEL_PATH)
    print("YOLO model loaded successfully.")
except Exception as e:
    print(f"FATAL: Could not load YOLO model. Error: {e}")
    model = None

def get_image_tags(image_path):
    if model is None:
        return ["Error: Model not loaded"]
    try:
        img = Image.open(image_path)
        img.convert('RGB').save(image_path, 'jpeg')
        results = model(image_path)
        names = model.names
        detected_classes = set()
        for r in results:
            for c in r.boxes.cls:
                detected_classes.add(names[int(c)])
        if not detected_classes:
            return ["Uncategorized"]
        return list(detected_classes)
    except Exception as e:
        print(f"Error processing image with YOLO model: {e}")
        return ["Error"]