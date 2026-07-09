"""
anpr/plate_recognition_yolo.py

Upgraded plate detection + OCR using YOLOv8 (Ultralytics) + EasyOCR.
Requires a license-plate-specific YOLOv8 model file placed at
anpr/license_plate_detector.pt (see README for how to get one free).
"""

import cv2
import re
import os
from ultralytics import YOLO

MODEL_PATH = "anpr/license_plate_detector.pt"
CONFIDENCE_THRESHOLD = 0.4

_reader = None
_model = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def _get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"YOLOv8 plate detection model not found at '{MODEL_PATH}'. "
                f"Download a free pretrained one from Roboflow Universe."
            )
        _model = YOLO(MODEL_PATH)
    return _model


def clean_plate_text(text):
    return re.sub(r"[^A-Za-z0-9]", "", text).upper()


def recognize_plate(image_path):
    model = _get_model()
    reader = _get_reader()

    image = cv2.imread(image_path)
    if image is None:
        return None, None

    results = model(image, verbose=False)[0]

    best_box = None
    best_confidence = 0
    for box in results.boxes:
        confidence = float(box.conf[0])
        if confidence > CONFIDENCE_THRESHOLD and confidence > best_confidence:
            best_confidence = confidence
            best_box = box.xyxy[0].cpu().numpy().astype(int)

    if best_box is None:
        return None, None

    x1, y1, x2, y2 = best_box
    plate_crop = image[y1:y2, x1:x2]

    if plate_crop.size == 0:
        return None, None

    plate_crop = cv2.resize(plate_crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    crop_path = image_path.rsplit(".", 1)[0] + "_plate_crop.jpg"
    cv2.imwrite(crop_path, plate_crop)

    ocr_results = reader.readtext(plate_crop)
    if not ocr_results:
        return None, crop_path

    combined_text = "".join([res[1] for res in ocr_results])
    cleaned = clean_plate_text(combined_text)

    if len(cleaned) < 4:
        return None, crop_path

    return cleaned, crop_path