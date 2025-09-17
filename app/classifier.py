import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "tool_classifier.h5")
model = tf.keras.models.load_model(MODEL_PATH)
CLASS_NAMES = ["spanner", "screwdriver", "hammer", "bolt", "nut", "clamp", "pliers", "drill"]
print(f"[INFO] Model loaded successfully from {MODEL_PATH}")

def classify_image(filepath):
    img = image.load_img(filepath, target_size=(128, 128))  # must match training size
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    preds = model.predict(img_array)
    print(f"[DEBUG] Predictions: {preds}")

    class_idx = np.argmax(preds[0])
    confidence = float(preds[0][class_idx])
    predicted_class = CLASS_NAMES[class_idx]
    print(f"[DEBUG] Predicted class: {predicted_class}, Confidence: {confidence}")
    
    return predicted_class, confidence
