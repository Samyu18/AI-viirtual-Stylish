import os
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
import logging
import math

# Suppress TensorFlow & oneDNN warnings
# import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

tf.get_logger().setLevel(logging.ERROR)
logging.getLogger("tensorflow").setLevel(logging.ERROR)

# Initialize MediaPipe Pose model
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

# Clothing Size Chart (Shoulder Width & Height in cm)
SIZE_CHART = {
    "S": (38, 150),
    "M": (42, 160),
    "L": (46, 170),
    "XL": (50, 180),
    "XXL": (54, 190),
    "XXXL": (58, 200),
}

def calculate_distance(point1, point2, image_width, image_height):
    """Calculate Euclidean distance between two normalized points in pixels."""
    x1, y1 = int(point1.x * image_width), int(point1.y * image_height)
    x2, y2 = int(point2.x * image_width), int(point2.y * image_height)
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)  # Euclidean distance formula

def estimate_size(image_path):
    """Detects a person from an image and estimates their clothing size."""
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print("❌ Error: Unable to load image. Check the file path.")
        return

    # Convert to RGB for MediaPipe
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    # Check if a person is detected
    if not results.pose_landmarks:
        print("⚠️ Error: No person detected in the image.")
        return

    # Extract key landmarks
    landmarks = results.pose_landmarks.landmark
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    nose = landmarks[mp_pose.PoseLandmark.NOSE]  # Head reference
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]

    # Image dimensions
    height, width, _ = image.shape

    # Compute **Shoulder Width** using Euclidean distance
    shoulder_width_pixels = calculate_distance(left_shoulder, right_shoulder, width, height)

    # Compute **Body Height** using head-to-ankle distance
    head_to_ankle_pixels = calculate_distance(nose, left_ankle, width, height)
    
    # Set an estimated real-world height for reference scaling (170 cm)
    real_world_height_cm = 170
    pixel_to_cm_ratio = real_world_height_cm / head_to_ankle_pixels

    # Convert pixel measurements to cm
    shoulder_width_cm = shoulder_width_pixels * pixel_to_cm_ratio
    body_height_cm = head_to_ankle_pixels * pixel_to_cm_ratio

    print(f"\n📏 **Detected Measurements:**")
    print(f"🔹 Shoulder Width: {shoulder_width_cm:.2f} cm")
    print(f"🔹 Body Height: {body_height_cm:.2f} cm")

    # Determine clothing size from chart
    predicted_size = "XXXL"
    for size, (sw, h) in SIZE_CHART.items():
        if shoulder_width_cm <= sw and body_height_cm <= h:
            predicted_size = size
            break

    print(f"\n✅ **Predicted Clothing Size: {predicted_size}**\n")

    return predicted_size

# Take image path input from terminal
# image_path = input("📂 Enter the image file path: ").strip()
estimate_size("C:/Users/APPLE/OneDrive/Desktop/Rtrp/fat.jpg")  # Run the function
