import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

# Load Trained Model
model = load_model("skin_tone_model.h5")

# Define Skin Tone Labels
SKIN_TONE_LABELS = ["Very Pale White", "White", "Fair", "Light Brown", "Brown", "Dark Brown / Black"]

def detect_skin_tone(image_path):
    """Predicts skin tone from an image."""
    image = cv2.imread(image_path)
    image = cv2.resize(image, (224, 224))
    image = img_to_array(image) / 255.0
    image = np.expand_dims(image, axis=0)

    # Predict Skin Tone
    prediction = model.predict(image)
    skin_tone = SKIN_TONE_LABELS[np.argmax(prediction)]

    return skin_tone

# Test on an image
test_image = "test_image.jpg"  # Place a test image in the same folder
predicted_skin_tone = detect_skin_tone(test_image)
print("Detected Skin Tone:", predicted_skin_tone)
