"""
anpr/plate_recognition.py

Number plate detection + text extraction, using:
- OpenCV -- image preprocessing and locating plate-like rectangular regions
- Tesseract OCR (via pytesseract) -- free, open-source text recognition
"""

import cv2
import pytesseract
import re
from config import Config

pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD


def clean_plate_text(text):
    return re.sub(r"[^A-Za-z0-9]", "", text).upper()


def find_plate_candidates(gray_image):
    blurred = cv2.bilateralFilter(gray_image, 11, 17, 17)
    edged = cv2.Canny(blurred, 30, 200)

    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]

    candidates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h) if h > 0 else 0
        area = w * h
        if 2.0 < aspect_ratio < 6.0 and area > 1500:
            candidates.append((x, y, w, h))

    return candidates


def recognize_plate(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return None, None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    candidates = find_plate_candidates(gray)
    print(f"[DEBUG] Found {len(candidates)} plate candidates: {candidates}")

    best_text = None
    best_crop_path = None

    for (x, y, w, h) in candidates:
        crop = gray[y:y + h, x:x + w]
        crop = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        crop = cv2.threshold(crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        raw_text = pytesseract.image_to_string(
            crop, config="--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        )
        cleaned = clean_plate_text(raw_text)
        print(f"[DEBUG] Candidate region {(x, y, w, h)} -> raw OCR: '{raw_text.strip()}' -> cleaned: '{cleaned}'")

        if cleaned and len(cleaned) >= 4:
            best_text = cleaned
            crop_path = image_path.rsplit(".", 1)[0] + "_plate_crop.jpg"
            cv2.imwrite(crop_path, crop)
            best_crop_path = crop_path
            break

    return best_text, best_crop_path