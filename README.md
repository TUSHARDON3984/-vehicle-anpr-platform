Vehicle ANPR Platform (Automatic Number Plate Recognition)
A full-stack web application that recognizes vehicle number plates from photos using a custom-trained YOLOv8 model, instantly looks up the owner's details from a database, and gates access behind email verification AND live face recognition -- all built with free, open-source tools.

Features
User registration with email verification (via Gmail SMTP)
Face ID login -- after password verification, a live webcam capture confirms the person logging in matches their registered face before access is granted
Custom-trained YOLOv8 plate detector -- trained from scratch on a license plate dataset (not a generic pretrained model)
EasyOCR text extraction -- reads plate text from the detected region
Instant owner lookup -- matches scanned plates against a vehicle registry and displays owner name, contact, address, and vehicle details
Manual vehicle registration -- add vehicles to the database directly
Full audit logging -- every scan is timestamped and recorded
Themed, animated UI -- black/yellow "road & traffic" visual theme with a parallax car illustration that moves based on scroll position and navigation direction, plus an animated particle background
Tech stack (all free & open source)
Purpose	Tool
Web framework	Flask
Database ORM	Flask-SQLAlchemy (SQLite)
Auth / sessions	Flask-Login
Email	Flask-Mail (Gmail SMTP)
Plate detection	YOLOv8 (Ultralytics) -- custom-trained
Plate OCR	EasyOCR
Face verification	OpenCV LBPH Face Recognizer
Frontend	HTML/CSS/JS (vanilla, no framework)
Project structure

vehicle_anpr_project/
├── app.py                       # Flask app factory / entry point
├── config.py                    # settings (reads from .env)
├── extensions.py                # db, login_manager, mail instances
├── models.py                    # User, Vehicle, ScanLog database models
├── requirements.txt
├── train_plate_model.py         # trains the custom YOLOv8 plate detector
├── download_dataset.py          # downloads training dataset via Roboflow API
│
├── anpr/
│   ├── plate_recognition.py       # classical OpenCV+Tesseract approach (fallback)
│   └── plate_recognition_yolo.py  # YOLOv8 + EasyOCR approach (primary)
│
├── face_auth/
│   └── recognizer.py             # face capture, training, verification (LBPH)
│
├── routes/
│   ├── auth.py                    # register, login, logout, email verification
│   ├── main.py                    # dashboard, scan, vehicle registry, history
│   └── face_auth.py               # Face ID setup + login verification
│
├── templates/                    # HTML pages (Jinja2)
├── static/
│   ├── css/style.css              # themed styling
│   ├── js/effects.js              # parallax car + particle animations
│   ├── faces/                     # per-user face photos (gitignored)
│   └── uploads/                   # scanned plate images (gitignored)
│
└── plate_dataset/                # training data (gitignored, regenerate via download_dataset.py)
Setup
1. Clone the repo

bash
git clone https://github.com/TUSHARDON3984/-vehicle-anpr-platform.git
cd -vehicle-anpr-platform
2. Create a virtual environment (Python 3.12 recommended)

bash
py -3.12 -m venv venv
venv\Scripts\activate
3. Install dependencies

bash
pip install -r requirements.txt
Note: if you hit an opencv-python / opencv-contrib-python conflict (both installed at once breaks the cv2.face module used for Face ID), fix it with:


bash
pip uninstall opencv-python opencv-python-headless -y
pip install --force-reinstall opencv-contrib-python==4.10.0.84
4. Set up your .env file
Create a .env file in the project root:


SECRET_KEY=your-random-secret-key
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_16_character_app_password
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
MAIL_PASSWORD must be a Gmail App Password (not your normal password) -- create one at https://myaccount.google.com/apppasswords (requires 2-Step Verification enabled on your Google account).

5. (Optional) Install Tesseract OCR
Only needed if using the fallback classical approach (anpr/plate_recognition.py). Download from https://github.com/UB-Mannheim/tesseract/wiki

6. Train your own YOLOv8 plate detector
The trained model isn't included in the repo (too large / regeneratable). To create it:


bash
pip install roboflow
python download_dataset.py    # downloads the training dataset
python train_plate_model.py   # trains and saves anpr/license_plate_detector.pt
Training on CPU takes roughly 1-4+ hours depending on dataset size/epochs (tune EPOCHS, IMAGE_SIZE, and fraction in train_plate_model.py to balance speed vs. accuracy).

7. Run the app

bash
python app.py
Visit http://127.0.0.1:5000

How it works (user flow)
Register an account -> verification email sent
Click the link in the email -> account verified
Log in with email + password
(First time) Go to "Set Up Face ID" -> webcam captures 5 photos -> trains your personal face profile
Log out and log back in -> after password check, you're now sent to a live face verification step -> only a matching face completes login
Register vehicles manually (plate number + owner details)
Scan a plate photo -> YOLOv8 detects the plate region -> EasyOCR reads the text -> instantly matched against the vehicle registry
View Scan History for a full audit trail
How the plate recognition works
Detection: A YOLOv8 nano model, fine-tuned specifically on license plate images (not the generic pretrained weights), locates the plate's bounding box in the photo
OCR: The cropped, upscaled plate region is passed to EasyOCR, a deep-learning text recognizer more tolerant of font/lighting variation than classical OCR
Lookup: The cleaned plate text is matched against the Vehicle table; a match displays full owner details, no match offers to register the vehicle
Every scan (matched or not) is logged with a timestamp for audit purposes
How Face ID verification works
Setup: 5 webcam photos are captured, face regions detected and cropped (Haar Cascade), normalized (resize + histogram equalization), and used to train a shared LBPH (Local Binary Patterns Histogram) model across all users
Login: after password verification succeeds, the user is NOT logged in yet -- their user ID is stored as "pending" in the session, and they're redirected to a live face capture page
A fresh webcam snapshot is compared against the trained model; only if it matches the pending user's ID (within a confidence threshold) does login_user() actually get called, completing the login
Known limitations
OCR accuracy depends on image quality -- clear, front-on, well-lit photos work best
YOLOv8 model was trained with a reduced dataset fraction and modest epoch count for reasonable CPU training time; increase EPOCHS and fraction in train_plate_model.py for higher accuracy if you have more time/compute
LBPH face recognition can struggle with visually similar faces (e.g. identical twins) and is sensitive to lighting consistency between setup and login
SQLite is used for simplicity; consider PostgreSQL/MySQL for a production/multi-user deployment
This is a local development setup (debug=True) -- disable debug mode and use a production WSGI server (e.g. gunicorn/waitress) before any real deployment
Camera access in browsers normally requires HTTPS, but localhost is treated as a secure context, so this works fine for local development
Security notes
Passwords are hashed with Werkzeug's generate_password_hash
Email verification tokens are signed and expire after 1 hour
Face verification acts as a genuine second factor -- password alone is insufficient once Face ID is set up
.env, the database, uploaded images, and face photos are all excluded from version control via .gitignore
Real-world use case
This mirrors systems used in parking management, gated communities, and toll systems: a camera (or uploaded photo) reads a plate, the system checks a database, and instantly surfaces who the vehicle belongs to -- replacing a manual, paper-based lookup process. The face verification layer adds an extra security dimension suited to contexts where only specific authorized personnel should be able to perform vehicle lookups.
