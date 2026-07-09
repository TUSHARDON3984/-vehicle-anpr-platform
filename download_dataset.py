from roboflow import Roboflow

rf = Roboflow(api_key="fHgeBIZJ7ytodxSnP6d1")
project = rf.workspace("roboflow-universe-projects").project("license-plate-recognition-rxg4e")
dataset = project.version(4).download("yolov8", location="plate_dataset")

print("Download complete! Dataset saved to plate_dataset/")