"""
train_plate_model.py

Trains a small YOLOv8 model to detect license plates, using the dataset
downloaded into plate_dataset/.

Usage:
    python train_plate_model.py

After training finishes, it automatically copies the best weights to
anpr/license_plate_detector.pt, ready for the Flask app to use.
"""

import shutil
import os
from ultralytics import YOLO

DATA_YAML = "plate_dataset/data.yaml"
EPOCHS = 10
IMAGE_SIZE = 416

def main():
    if not os.path.exists(DATA_YAML):
        print(f"ERROR: Could not find {DATA_YAML}. Make sure plate_dataset/ exists.")
        return

    print("Starting training... this will take a while on CPU (expect 30-90+ minutes). Let it run.")

    model = YOLO("yolov8n.pt")
    results = model.train(data=DATA_YAML, epochs=EPOCHS, imgsz=IMAGE_SIZE, batch=8, fraction=0.15)

    train_dir = results.save_dir
    best_weights = os.path.join(train_dir, "weights", "best.pt")

    if os.path.exists(best_weights):
        os.makedirs("anpr", exist_ok=True)
        shutil.copy(best_weights, "anpr/license_plate_detector.pt")
        print(f"\nDone! Trained model copied to anpr/license_plate_detector.pt")
    else:
        print(f"WARNING: Could not find {best_weights}. Check the runs/detect/ folder manually.")


if __name__ == "__main__":
    main()