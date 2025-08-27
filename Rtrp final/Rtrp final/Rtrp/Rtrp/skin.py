from flask import Flask, request, jsonify, send_file, render_template
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def extract_skin(image):
    """Extracts the skin area from an image using YCrCb color filtering."""
    image_ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    lower = np.array([0, 133, 77], dtype=np.uint8)
    upper = np.array([255, 173, 127], dtype=np.uint8)
    mask = cv2.inRange(image_ycrcb, lower, upper)
    skin = cv2.bitwise_and(image, image, mask=mask)
    return skin

def get_dominant_color(image, k=3):
    """Finds the dominant color in the given image using KMeans clustering."""
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixels = image.reshape(-1, 3)
    pixels = pixels[np.any(pixels != [0, 0, 0], axis=1)]  # Remove black (non-skin) pixels

    if len(pixels) == 0:
        return np.array([0, 0, 0])  # Return black if no skin pixels are found

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(pixels)
    dominant_color = kmeans.cluster_centers_[np.argmax(np.bincount(kmeans.labels_))]  
    return dominant_color.astype(int)

def classify_skin_tone(color):
    """Classifies the detected dominant skin color into predefined skin tone categories."""
    skin_tones = {
        "Fair": [(220, 184, 153), (255, 224, 189)],
        "Light": [(194, 154, 125), (222, 184, 135)],
        "Medium": [(151, 107, 83), (177, 120, 90)],
        "Tan": [(125, 80, 60), (153, 101, 80)],
        "Deep": [(85, 52, 42), (114, 74, 60)]
    }

    min_distance = float("inf")
    best_match = "Unknown"

    for tone, (lower, upper) in skin_tones.items():
        lower, upper = np.array(lower), np.array(upper)
        avg_color = (lower + upper) / 2
        distance = np.linalg.norm(avg_color - color)

        if distance < min_distance:
            min_distance = distance
            best_match = tone

    return best_match

@app.route('/')
def index():
    """Redirects to indo.html instead of index.html"""
    return render_template("indo.html")

@app.route('/indo')
def indo():
    """Serves indo.html explicitly when accessed"""
    return render_template("indo.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles image upload, extracts skin, detects skin tone, and returns results."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    image = cv2.imread(file_path)
    if image is None:
        return jsonify({"error": "Invalid image"}), 400
    
    # Process the image
    skin = extract_skin(image)
    dominant_color = get_dominant_color(skin)
    skin_tone = classify_skin_tone(dominant_color)

    # Save skin image
    result_path = os.path.join(RESULT_FOLDER, file.filename)
    cv2.imwrite(result_path, skin)

    return jsonify({
        "skin_tone": skin_tone,
        "dominant_color": dominant_color.tolist(),
        "skin_image": f"/get_skin/{file.filename}"
    })

@app.route('/get_skin/<filename>')
def get_skin(filename):
    """Returns the extracted skin image."""
    return send_file(os.path.join(RESULT_FOLDER, filename), mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
