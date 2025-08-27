import cv2
import numpy as np
import mediapipe as mp
from flask import Flask, request, render_template
import os
from sklearn.cluster import KMeans
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Mediapipe models
mp_pose = mp.solutions.pose
mp_face = mp.solutions.face_detection
pose = mp_pose.Pose()
face_detection = mp_face.FaceDetection()

# Define Skin Tone Ranges (in LAB color space for better accuracy)
SKIN_TONES = {
    "Type I": (240, 128, 128),
    "Type II": (220, 138, 128),
    "Type III": (200, 148, 128),
    "Type IV": (180, 158, 128),
    "Type V": (160, 168, 128),
    "Type VI": (120, 178, 128)
}

# Define Body Shape Categories
# Updated Skin Tone Ranges with Names
SKIN_TONES = {
    "Very Pale White": (240, 128, 128),
    "White": (220, 138, 128),
    "Fair": (200, 148, 128),
    "Light Brown": (180, 158, 128),
    "Brown": (160, 168, 128),
    "Dark Brown / Black": (120, 178, 128)
}

def detect_skin_tone(image):
    """Extract skin tone using K-Means clustering on forehead region."""
    h, w, _ = image.shape
    face = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if face.detections:
        for detection in face.detections:
            bbox = detection.location_data.relative_bounding_box
            x, y, width, height = int(bbox.xmin * w), int(bbox.ymin * h), int(bbox.width * w), int(bbox.height * h)

            if width == 0 or height == 0:
                return "Unknown"

            # Extract forehead region (top 20% of face)
            forehead_y1 = max(y + int(height * 0.15), 0)
            forehead_y2 = min(y + int(height * 0.3), h)
            forehead_region = image[forehead_y1:forehead_y2, x:x+width]

            if forehead_region.size == 0:
                return "Unknown"

            # Convert to LAB color space
            forehead_lab = cv2.cvtColor(forehead_region, cv2.COLOR_BGR2LAB)
            pixels = forehead_lab.reshape(-1, 3)

            # Apply K-Means clustering
            kmeans = KMeans(n_clusters=1, random_state=42, n_init=10).fit(pixels)
            dominant_color = kmeans.cluster_centers_[0]

            # Find closest skin tone in LAB space
            closest_tone = min(SKIN_TONES, key=lambda k: np.linalg.norm(dominant_color - np.array(SKIN_TONES[k])))

            return closest_tone

    return "Unknown"


def detect_body_shape(image):
    """Estimate body shape using Mediapipe Pose landmarks."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        image_width = image.shape[1]

        # Get key widths
        shoulder_width = abs(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x - 
                             landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x) * image_width
        waist_width = abs(landmarks[mp_pose.PoseLandmark.LEFT_HIP].x - 
                          landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x) * image_width
        hip_width = abs(landmarks[mp_pose.PoseLandmark.LEFT_HIP].x - 
                        landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x) * image_width

        # **Key Ratios for Shape Identification**
        shoulder_to_hip_ratio = shoulder_width / hip_width
        waist_to_hip_ratio = waist_width / hip_width
        waist_to_shoulder_ratio = waist_width / shoulder_width

        # **Classification Logic**
        if waist_to_shoulder_ratio < 0.75 and waist_to_hip_ratio < 0.75:
            return "Hourglass"
        elif waist_to_shoulder_ratio < 0.8 and waist_to_hip_ratio > 0.9:
            return "Bottom Hourglass"
        elif waist_to_shoulder_ratio > 0.8 and waist_to_hip_ratio < 0.9:
            return "Top Hourglass"
        elif shoulder_to_hip_ratio > 1.15:
            return "Invertedd Triangle"
        elif shoulder_to_hip_ratio < 0.85:
            return "Triangle (Pear)"
        elif 0.9 <= waist_to_shoulder_ratio <= 1.1 and 0.9 <= waist_to_hip_ratio <= 1.1:
            return "Rectangle"
        else:
            return "Round (Apple)"

    return "Unknown"


@app.route("/", methods=["GET", "POST"])
def upload_image():
    """Web interface to upload image and detect skin tone & body shape."""
    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded"
        
        file = request.files["file"]
        if file.filename == "":
            return "No file selected"
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        if not os.path.exists(filepath):
            return "Error saving file. Please try again."

        image = cv2.imread(filepath)
        skin_tone = detect_skin_tone(image)
        body_shape = detect_body_shape(image)

        return render_template("result.html", image_url=filepath, skin_tone=skin_tone, body_shape=body_shape)

    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)
