#train_model.py

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import json
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_DIR = os.path.join(BASE_DIR, "..", "datasets", "train")
VAL_DIR = os.path.join(BASE_DIR, "..", "datasets", "validation")
MODEL_PATH = os.path.join(BASE_DIR, "tool_classifier.h5")
CLASS_IDX_PATH = os.path.join(BASE_DIR, "class_indices.json")

# Data generators
train_datagen = ImageDataGenerator(rescale=1./255)
val_datagen = ImageDataGenerator(rescale=1./255)

train_gen = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(128, 128),
    batch_size=32,
    class_mode="categorical"
)

val_gen = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=(128, 128),
    batch_size=32,
    class_mode="categorical"
)

# Build CNN model
model = Sequential([
    Conv2D(32, (3, 3), activation="relu", input_shape=(128, 128, 3)),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), activation="relu"),
    MaxPooling2D(2, 2),
    Flatten(),
    Dense(128, activation="relu"),
    Dropout(0.4),
    Dense(train_gen.num_classes, activation="softmax")
])

model.compile(optimizer=Adam(learning_rate=0.0005),
              loss="categorical_crossentropy",
              metrics=["accuracy"])

# Train
history = model.fit(train_gen, validation_data=val_gen, epochs=10)

# Save model + class indices
model.save(MODEL_PATH)
with open(CLASS_IDX_PATH, "w") as f:
    json.dump(train_gen.class_indices, f)

print(f"✅ Training complete. Model saved at {MODEL_PATH}")
