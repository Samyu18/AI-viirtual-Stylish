from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
import skin  # Import your skin tone detection script

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Save uploaded image
        if "image" not in request.files:
            return "Error: No image uploaded.", 400
        file = request.files["image"]
        if file.filename == "":
            return "Error: No selected file.", 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Detect skin tone using `skin.py`
        detected_skin_tone = skin.detect_skin_tone(filepath)

        selected_gender = request.form.get("gender")
        selected_body_shape = request.form.get("body_shape")
        selected_size = request.form.get("size")
        selected_height = request.form.get("height")
        selected_weight = request.form.get("weight")

        if not all([detected_skin_tone, selected_gender, selected_body_shape, selected_size, selected_height, selected_weight]):
            return "Error: Please fill in all required fields.", 400

        # Get color and dress recommendations
        color_recommendations = skin_tones.get(detected_skin_tone, [])
        dress_recommendations = body_shapes_men[selected_body_shape] if selected_gender == "Men" else body_shapes_women[selected_body_shape]

        return render_template(
            "result.html",
            skin_tone=detected_skin_tone,
            gender=selected_gender,
            body_shape=selected_body_shape,
            size=selected_size,
            height=selected_height,
            weight=selected_weight,
            colors=color_recommendations,
            dresses=dress_recommendations
        )

    return render_template("index.html", sizes=sizes, heights=heights, weights=weights)

if __name__ == "__main__":
    app.run(debug=True)
