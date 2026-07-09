"""
face_auth/recognizer.py

Face capture, training, and verification using OpenCV's LBPH recognizer.
"""

import cv2
import numpy as np
import os
import base64

FACES_DIR = "static/faces"
MODEL_PATH = "face_auth/face_model.yml"
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
CONFIDENCE_THRESHOLD = 70

_face_detector = cv2.CascadeClassifier(CASCADE_PATH)


def decode_base64_image(data_url):
    header, encoded = data_url.split(",", 1)
    binary_data = base64.b64decode(encoded)
    np_arr = np.frombuffer(binary_data, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)


def _extract_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = _face_detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    if len(faces) == 0:
        return None
    (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
    face_crop = cv2.resize(gray[y:y + h, x:x + w], (200, 200))
    face_crop = cv2.equalizeHist(face_crop)
    return face_crop


def save_face_images(user_id, data_url_images):
    user_dir = os.path.join(FACES_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    saved_count = 0
    for i, data_url in enumerate(data_url_images):
        image = decode_base64_image(data_url)
        face_crop = _extract_face(image)
        if face_crop is not None:
            filename = os.path.join(user_dir, f"face_{i}.jpg")
            cv2.imwrite(filename, face_crop)
            saved_count += 1

    return saved_count


def train_model():
    faces = []
    labels = []

    if not os.path.exists(FACES_DIR):
        return False

    for user_id_str in os.listdir(FACES_DIR):
        user_dir = os.path.join(FACES_DIR, user_id_str)
        if not os.path.isdir(user_dir):
            continue
        try:
            user_id = int(user_id_str)
        except ValueError:
            continue

        for filename in os.listdir(user_dir):
            if filename.endswith(".jpg"):
                img_path = os.path.join(user_dir, filename)
                face_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if face_img is not None:
                    faces.append(face_img)
                    labels.append(user_id)

    if len(faces) == 0:
        return False

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))
    recognizer.write(MODEL_PATH)
    return True


def verify_face(data_url_image, expected_user_id):
    if not os.path.exists(MODEL_PATH):
        return False, None, "No face model trained yet."

    image = decode_base64_image(data_url_image)
    face_crop = _extract_face(image)

    if face_crop is None:
        return False, None, "No face detected in the frame. Make sure your face is clearly visible."

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)

    predicted_label, confidence = recognizer.predict(face_crop)

    if predicted_label == expected_user_id and confidence < CONFIDENCE_THRESHOLD:
        return True, confidence, "Face verified successfully."
    elif predicted_label != expected_user_id:
        return False, confidence, "Face does not match the account. Verification failed."
    else:
        return False, confidence, "Face match too uncertain. Try again with better lighting."