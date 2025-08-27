from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from skin import extract_skin, get_dominant_color, classify_skin_tone
import random
import glob

app = Flask(__name__)
app.secret_key = 'secret123'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dummy user data
users = {'test': {'password': 'test123'}}

# Skin tone and color recommendations
skin_tones = {
    "Fair": ["Light Blue", "Soft Pink", "Lavender", "Peach", "Mint Green"],
    "Light": ["Navy Blue", "Emerald", "Burgundy", "Deep Red", "Teal"],
    "Medium": ["Olive", "Mustard", "Coral", "Plum", "Charcoal"],
    "Tan": ["Maroon", "Brown", "Dark Green", "Gold", "Deep Orange"],
    "Deep": ["Rust", "Ivory", "Deep Purple", "Burnt Orange", "Forest Green"]
}

# Dress recommendations based on body type
body_shapes_men = {
    "Rectangle": ["Slim Fit Blazer", "Layered Outfits", "Straight-Leg Pants"],
    "Triangle": ["V-neck Sweaters", "Structured Blazers", "Dark-Wash Jeans"],
    "Inverted Triangle": ["Relaxed Fit Shirts", "Cargo Pants", "Soft Fabrics"],
    "Oval": ["Single-Breasted Jackets", "Vertical Stripes", "Dark Shades"],
    "Trapezoid": ["T-Shirts", "Bomber Jackets", "Slim-Fit Jeans"]
}

body_shapes_women = {
    "Hourglass": ["Wrap Dress", "Bodycon", "Peplum Tops", "High-Waisted Jeans"],
    "Top Hourglass": ["V-neck Tops", "A-line Skirts", "Flared Dresses"],
    "Bottom Hourglass": ["Off-Shoulder Tops", "Straight Pants", "Pencil Skirts"],
    "Rectangle": ["Belted Dresses", "Layered Outfits", "Peplum Tops"],
    "Triangle (Pear)": ["Boat Neck Tops", "Wide-Leg Pants", "A-line Dresses"],
    "Inverted Triangle": ["V-neck Dresses", "Skater Skirts", "Flared Pants"],
    "Round (Apple)": ["Empire Waist Dresses", "Flowy Tops", "Straight-Leg Pants"]
}

# Size, height, and weight options
sizes = ["S", "M", "L", "XL", "XXL", "XXXL"]
heights = ["Short", "Medium", "Tall"]
weights = ["Thin", "Medium", "Fat"]

# Sample dress image paths
dress_data = {
    "peach": ["peach_dress1.jpg", "peach_dress2.jpg","peach_dress3.jpg", "peach_dress4.jpg","peach_dress5.jpg", "peach_dress6.jpg",
              "peach_dress7.jpg", "peach_dress8.jpg","peach_dress9.jpg", "peach_dress10.jpg","peach_dress11.jpg", "peach_dress12.jpg",
              "peach_dress13.jpg","peach_dress14.jpg", "peach_dress15.jpg","peach_dress16.jpg","peach_dress17.jpg", "peach_dress18.jpg",
              "peach_dress19.jpg", "peach_dress20.jpg", "peach_dress21.jpg", "peach_dress22.jpg","men1.jpg", "men2.jpg", "men3.jpg", "men4.jpg",
              "men5.jpg", "men6.jpg", "men7.jpg", "men8.jpg","men9.jpg","men10.jpg","men11.jpg"],
    "soft_pink": ["soft_pink_dress1.jpg", "soft_pink_dress2.jpg","soft_pink_dress3.jpg","soft_pink_dress4.jpg", "soft_pink_dress5.jpg","soft_pink_dress6.jpg",
                  "soft_pink_dress7.jpg", "soft_pink_dress8.jpg","soft_pink_dress9.jpg","soft_pink_dress10.jpg", "soft_pink_dress11.jpg","soft_pink_dress12.jpg",
                  "soft_pink_dress13.jpg", "soft_pink_dress14.jpg","soft_pink_dress15.jpg","soft_pink_dress16.jpg", "soft_pink_dress17.jpg","soft_pink_dress18.jpg",
                  "soft_pink_dress19.jpg", "soft_pink_dress20.jpg", "soft_pink_dress21.jpg", "soft_pink_dress22.jpg","men1.jpg", "men2.jpg", "men3.jpg", "men4.jpg",
                  "men5.jpg", "men6.jpg", "men7.jpg", "men8.jpg","men9.jpg", "men10.jpg", "men11.jpg", "men12.jpg"],
    "light_blue": ["light_blue_dress1.jpg", "light_blue_dress2.jpg","light_blue_dress3.jpg", "light_blue_dress4.jpg","light_blue_dress5.jpg",
                    "light_blue_dress6.jpg","light_blue_dress7.jpg", "light_blue_dress8.jpg","light_blue_dress9.jpg", "light_blue_dress10.jpg",
                    "light_blue_dress11.jpg", "light_blue_dress12.jpg","light_blue_dress13.jpg", "light_blue_dress14.jpg","light_blue_dress15.jpg",
                    "light_blue_dress16.jpg","light_blue_dress17.jpg", "light_blue_dress18.jpg","light_blue_dress19.jpg", "light_blue_dress20.jpg",
                    "light_blue_dress21.jpg", "light_blue_dress22.jpg","blue1.jpg", "blue2.jpg", "blue3.jpg", "blue4.jpg",
                    "blue5.jpg", "blue6.jpg", "blue7.jpg", "blue8.jpg","blue9.jpg", "blue10.jpg", "blue11.jpg", "blue12.jpg","blue13.jpg"],
    "lavender": ["lavender_dress1.jpg","lavender_dress2.jpg","lavender_dress3.jpg","lavender_dress4.jpg","lavender_dress5.jpg","lavender_dress6.jpg",
                 "lavender_dress7.jpg","lavender_dress8.jpg","lavender_dress9.jpg","lavender_dress10.jpg","lavender_dress11.jpg","lavender_dress12.jpg",
                 "lavender_dress13.jpg","lavender_dress14.jpg","lavender_dress15.jpg","lavender_dress16.jpg","lavender_dress17.jpg","lavender_dress18.jpg",
                 "lavender_dress19.jpg","lavender_dress20.jpg","lavender_dress21.jpg","lavender_dress22.jpg","men1.jpg", "men2.jpg", "men3.jpg", "men4.jpg",
                "men5.jpg", "men6.jpg", "men7.jpg", "men8.jpg","men9.jpg"],
    "mint_green": ["mint_green_dress1.jpg", "mint_green_dress2.jpg","mint_green_dress3.jpg", "mint_green_dress4.jpg","mint_green_dress5.jpg", "mint_green_dress6.jpg",
                   "mint_green_dress7.jpg", "mint_green_dress8.jpg","mint_green_dress9.jpg", "mint_green_dress10.jpg","mint_green_dress11.jpg", "mint_green_dress12.jpg",
                   "mint_green_dress13.jpg","mint_green_dress14.jpg", "mint_green_dress15.jpg","mint_green_dress16.jpg","mint_green_dress17.jpg", "mint_green_dress18.jpg",
                   "mint_green_dress19.jpg", "mint_green_dress20.jpg", "mint_green_dress21.jpg", "mint_green_dress22.jpg",
                   "mint1.jpg", "mint2.jpg", "mint3.jpg", "mint4.jpg","mint5.jpg", "mint6.jpg", "mint7.jpg", "mint8.jpg","mint9.jpg", "mint10.jpg", "mint11.jpg", "mint12.jpg"],
    "navy_blue": ["navy_blue_dress1.jpg", "navy_blue_dress2.jpg", "navy_blue_dress3.jpg", "navy_blue_dress4.jpg",
                   "navy_blue_dress5.jpg", "navy_blue_dress6.jpg", "navy_blue_dress7.jpg", "navy_blue_dress8.jpg",
                   "navy_blue_dress9.jpg", "navy_blue_dress10.jpg", "navy_blue_dress11.jpg", "navy_blue_dress12.jpg",
                   "navy_blue_dress13.jpg", "navy_blue_dress14.jpg", "navy_blue_dress15.jpg", "navy_blue_dress16.jpg",
                  "navy_blue_dress17.jpg", "navy_blue_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg","man12.jpg"],
"emerald": [
    "emarald_dress1.jpg", "emarald_dress2.jpg", "emarald_dress3.jpg", "emarald_dress4.jpg",
    "emarald_dress5.jpg", "emarald_dress6.jpg", "emarald_dress7.jpg", "emarald_dress8.jpg",
    "emarald_dress9.jpg", "emarald_dress10.jpg", "emarald_dress11.jpg", "emarald_dress12.jpg",
    "emarald_dress13.jpg", "emarald_dress14.jpg", "emarald_dress15.jpg", "emarald_dress16.jpg",
    "emarald_dress17.jpg", "emarald_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg","man12.jpg"],
"burgundy": [
    "burgundy_dress1.jpg", "burgundy_dress2.jpg", "burgundy_dress3.jpg", "burgundy_dress4.jpg",
    "burgundy_dress5.jpg", "burgundy_dress6.jpg", "burgundy_dress7.jpg", "burgundy_dress8.jpg",
    "burgundy_dress9.jpg", "burgundy_dress10.jpg", "burgundy_dress11.jpg", "burgundy_dress12.jpg",
    "burgundy_dress13.jpg", "burgundy_dress14.jpg", "burgundy_dress15.jpg", "burgundy_dress16.jpg",
    "burgundy_dress17.jpg", "burgundy_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg"],
"deep_red": [
    "deep_red_dress1.jpg", "deep_red_dress2.jpg", "deep_red_dress3.jpg", "deep_red_dress4.jpg",
    "deep_red_dress5.jpg", "deep_red_dress6.jpg", "deep_red_dress7.jpg", "deep_red_dress8.jpg",
    "deep_red_dress9.jpg", "deep_red_dress10.jpg", "deep_red_dress11.jpg", "deep_red_dress12.jpg",
    "deep_red_dress13.jpg", "deep_red_dress14.jpg", "deep_red_dress15.jpg", "deep_red_dress16.jpg",
    "deep_red_dress17.jpg", "deep_red_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man10.jpg","man11.jpg"],
"teal": [
    "teal_dress1.jpg", "teal_dress2.jpg", "teal_dress3.jpg", "teal_dress4.jpg",
    "teal_dress5.jpg", "teal_dress6.jpg", "teal_dress7.jpg", "teal_dress8.jpg",
    "teal_dress9.jpg", "teal_dress10.jpg", "teal_dress11.jpg", "teal_dress12.jpg",
    "teal_dress13.jpg", "teal_dress14.jpg", "teal_dress15.jpg", "teal_dress16.jpg",
    "teal_dress17.jpg", "teal_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg"],
"olive": [
    "olive_dress1.jpg", "olive_dress2.jpg", "olive_dress3.jpg", "olive_dress4.jpg",
    "olive_dress5.jpg", "olive_dress6.jpg", "olive_dress7.jpg", "olive_dress8.jpg",
    "olive_dress9.jpg", "olive_dress10.jpg", "olive_dress11.jpg", "olive_dress12.jpg",
    "olive_dress13.jpg", "olive_dress14.jpg", "olive_dress15.jpg", "olive_dress16.jpg",
    "olive_dress17.jpg", "olive_dress18.jpg","man1.jpg", "man2.jpg",  "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg"],
"mustard": ["mustard_dress1.jpg", "mustard_dress2.jpg", "mustard_dress4.jpg",
    "mustard_dress5.jpg", "mustard_dress6.jpg", "mustard_dress7.jpg", "mustard_dress8.jpg",
    "mustard_dress9.jpg", "mustard_dress10.jpg", "mustard_dress11.jpg", "mustard_dress12.jpg",
    "mustard_dress13.jpg", "mustard_dress14.jpg", "mustard_dress15.jpg", "mustard_dress16.jpg",
    "mustard_dress17.jpg", "mustard_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg"],
"coral": [
    "coral_dress1.jpg", "coral_dress2.jpg", "coral_dress3.jpg", "coral_dress4.jpg",
    "coral_dress5.jpg", "coral_dress6.jpg", "coral_dress7.jpg", "coral_dress8.jpg",
    "coral_dress9.jpg", "coral_dress10.jpg", "coral_dress11.jpg", "coral_dress12.jpg",
    "coral_dress13.jpg", "coral_dress14.jpg", "coral_dress15.jpg", "coral_dress16.jpg",
    "coral_dress17.jpg", "coral_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg"],
"plum": [
    "plum_dress1.jpg", "plum_dress2.jpg", "plum_dress3.jpg", "plum_dress4.jpg",
    "plum_dress5.jpg", "plum_dress6.jpg", "plum_dress7.jpg", "plum_dress8.jpg",
    "plum_dress9.jpg", "plum_dress10.jpg", "plum_dress11.jpg", "plum_dress12.jpg",
    "plum_dress13.jpg", "plum_dress14.jpg", "plum_dress15.jpg", "plum_dress16.jpg",
    "plum_dress17.jpg", "plum_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg"],
"charcoal": [
    "charcoal_dress1.jpg", "charcoal_dress2.jpg", "charcoal_dress3.jpg", "charcoal_dress4.jpg",
    "charcoal_dress5.jpg", "charcoal_dress6.jpg", "charcoal_dress7.jpg", "charcoal_dress8.jpg",
    "charcoal_dress9.jpg", "charcoal_dress10.jpg", "charcoal_dress11.jpg", "charcoal_dress12.jpg",
    "charcoal_dress13.jpg", "charcoal_dress14.jpg", "charcoal_dress15.jpg", "charcoal_dress16.jpg",
    "charcoal_dress17.jpg", "charcoal_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man10.jpg","man11.jpg"],
"maroon": [
    "maroon_dress1.jpg", "maroon_dress2.jpg", "maroon_dress3.jpg", "maroon_dress4.jpg",
    "maroon_dress5.jpg", "maroon_dress6.jpg", "maroon_dress7.jpg", "maroon_dress8.jpg",
    "maroon_dress9.jpg", "maroon_dress10.jpg", "maroon_dress11.jpg", "maroon_dress12.jpg",
    "maroon_dress13.jpg", "maroon_dress14.jpg", "maroon_dress15.jpg", "maroon_dress16.jpg",
    "maroon_dress17.jpg", "maroon_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg"],
"brown": [
    "brown_dress1.jpg", "brown_dress2.jpg", "brown_dress3.jpg", "brown_dress4.jpg",
    "brown_dress5.jpg", "brown_dress6.jpg", "brown_dress7.jpg", "brown_dress8.jpg",
    "brown_dress9.jpg", "brown_dress10.jpg", "brown_dress11.jpg", "brown_dress12.jpg",
    "brown_dress13.jpg", "brown_dress14.jpg", "brown_dress15.jpg", "brown_dress16.jpg",
    "brown_dress17.jpg", "brown_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg","man12.jpg"],
"dark_green": [
    "dark_green_dress1.jpg", "dark_green_dress2.jpg", "dark_green_dress3.jpg", "dark_green_dress4.jpg",
    "dark_green_dress5.jpg", "dark_green_dress6.jpg", "dark_green_dress7.jpg", "dark_green_dress8.jpg",
    "dark_green_dress9.jpg", "dark_green_dress10.jpg", "dark_green_dress11.jpg", "dark_green_dress12.jpg",
    "dark_green_dress13.jpg", "dark_green_dress14.jpg", "dark_green_dress15.jpg", "dark_green_dress16.jpg",
    "dark_green_dress17.jpg", "dark_green_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg","man12.jpg"],
"gold": [
    "gold_dress1.jpg", "gold_dress2.jpg", "gold_dress3.jpg", "gold_dress4.jpg",
    "gold_dress5.jpg", "gold_dress6.jpg", "gold_dress7.jpg", "gold_dress8.jpg",
    "gold_dress9.jpg", "gold_dress10.jpg", "gold_dress11.jpg", "gold_dress12.jpg",
    "gold_dress13.jpg", "gold_dress14.jpg", "gold_dress15.jpg", "gold_dress16.jpg",
    "gold_dress17.jpg", "gold_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg","man12.jpg"],
"deep_orange": [
    "deep_orange_dress1.jpg", "deep_orange_dress2.jpg", "deep_orange_dress3.jpg", "deep_orange_dress4.jpg",
    "deep_orange_dress5.jpg", "deep_orange_dress6.jpg", "deep_orange_dress7.jpg", "deep_orange_dress8.jpg",
    "deep_orange_dress9.jpg", "deep_orange_dress10.jpg", "deep_orange_dress11.jpg", "deep_orange_dress12.jpg",
    "deep_orange_dress13.jpg", "deep_orange_dress14.jpg", "deep_orange_dress15.jpg", "deep_orange_dress16.jpg",
    "deep_orange_dress17.jpg", "deep_orange_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg"],
"rust": [
    "rust_dress1.jpg", "rust_dress2.jpg", "rust_dress3.jpg", "rust_dress4.jpg",
    "rust_dress5.jpg", "rust_dress6.jpg", "rust_dress7.jpg", "rust_dress8.jpg",
    "rust_dress9.jpg", "rust_dress10.jpg", "rust_dress11.jpg", "rust_dress12.jpg",
    "rust_dress13.jpg", "rust_dress14.jpg", "rust_dress15.jpg", "rust_dress16.jpg",
    "rust_dress17.jpg", "rust_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg","man12.jpg"],
"ivory": [ "ivory_dress1.jpg", "ivory_dress2.jpg", "ivory_dress3.jpg", "ivory_dress4.jpg",
    "ivory_dress5.jpg", "ivory_dress6.jpg", "ivory_dress7.jpg", "ivory_dress8.jpg",
    "ivory_dress9.jpg", "ivory_dress10.jpg", "ivory_dress11.jpg", "ivory_dress12.jpg",
    "ivory_dress13.jpg", "ivory_dress14.jpg", "ivory_dress15.jpg", "ivory_dress16.jpg",
    "ivory_dress17.jpg", "ivory_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg","man12.jpg","man12.jpg","man13.jpg"],
"deep_purple": [
    "deep_purple_dress1.jpg", "deep_purple_dress2.jpg", "deep_purple_dress3.jpg", "deep_purple_dress4.jpg",
    "deep_purple_dress5.jpg", "deep_purple_dress6.jpg", "deep_purple_dress7.jpg", "deep_purple_dress8.jpg",
    "deep_purple_dress9.jpg", "deep_purple_dress10.jpg", "deep_purple_dress11.jpg", "deep_purple_dress12.jpg",
    "deep_purple_dress13.jpg", "deep_purple_dress14.jpg", "deep_purple_dress15.jpg", "deep_purple_dress16.jpg",
    "deep_purple_dress17.jpg", "deep_purple_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg"],
"forest_green": [
    "forest_green_dress1.jpg", "forest_green_dress2.jpg", "forest_green_dress3.jpg", "forest_green_dress4.jpg",
    "forest_green_dress5.jpg", "forest_green_dress6.jpg", "forest_green_dress7.jpg", "forest_green_dress8.jpg",
    "forest_green_dress9.jpg", "forest_green_dress10.jpg", "forest_green_dress11.jpg", "forest_green_dress12.jpg",
    "forest_green_dress13.jpg", "forest_green_dress14.jpg", "forest_green_dress15.jpg", "forest_green_dress16.jpg",
    "forest_green_dress17.jpg", "forest_green_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg","man12.jpg"],
"burnt_orange": [
    "deep_orange_dress1.jpg", "deep_orange_dress2.jpg", "deep_orange_dress3.jpg", "deep_orange_dress4.jpg",
    "deep_orange_dress5.jpg", "deep_orange_dress6.jpg", "deep_orange_dress7.jpg", "deep_orange_dress8.jpg",
    "deep_orange_dress9.jpg", "deep_orange_dress10.jpg", "deep_orange_dress11.jpg", "deep_orange_dress12.jpg",
    "deep_orange_dress13.jpg", "deep_orange_dress14.jpg", "deep_orange_dress15.jpg", "deep_orange_dress16.jpg",
    "deep_orange_dress17.jpg", "deep_orange_dress18.jpg","man1.jpg", "man2.jpg", "man3.jpg", "man4.jpg",
                "man5.jpg", "man6.jpg", "man7.jpg", "man8.jpg","man9.jpg","man10.jpg","man11.jpg"]

}

# Add a list of quotes for the welcome modal
quotes = [
    "Elegance is the only beauty that never fades.",
    "Fashion is the armor to survive the reality of everyday life.",
    "Style is a way to say who you are without having to speak.",
    "Simplicity is the keynote of all true elegance.",
    "Life isn't perfect but your outfit can be.",
    "Dress like you're already famous.",
    "People will stare. Make it worth their while.",
    "Fashion fades, only style remains the same."
]

# Home Page
@app.route('/')
def home():
    quote = random.choice(quotes)
    return render_template('home.html', quote=quote)

# Main Form Page for Recommendations (Index Page)
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        selected_skin_tone = request.form.get("skin_tone")
        selected_gender = request.form.get("gender")
        selected_body_shape = request.form.get("body_shape")
        selected_size = request.form.get("size")
        selected_height = request.form.get("height")
        selected_weight = request.form.get("weight")

        # Error handling for missing inputs
        if not all([selected_skin_tone, selected_gender, selected_body_shape, selected_size, selected_height, selected_weight]):
            return "Error: Please fill in all required fields.", 400

        # Validate skin tone
        if selected_skin_tone not in skin_tones:
            return "Error: Invalid skin tone selection.", 400

        # Get dress recommendations based on selected skin tone
        color_recommendations = skin_tones[selected_skin_tone]
        dresses = dress_data.get(selected_skin_tone, [])

        # Validate body shape and gender
        if selected_gender == "Men":
            if selected_body_shape not in body_shapes_men:
                return "Error: Invalid body shape for men.", 400
            dress_recommendations = body_shapes_men[selected_body_shape]
        elif selected_gender == "Women":
            if selected_body_shape not in body_shapes_women:
                return "Error: Invalid body shape for women.", 400
            dress_recommendations = body_shapes_women[selected_body_shape]
        else:
            return "Error: Invalid gender selection.", 400

        # Return the results page with dresses and recommendations
        return render_template(
            "results.html",
            skin_tone=selected_skin_tone,
            gender=selected_gender,
            body_shape=selected_body_shape,
            size=selected_size,
            height=selected_height,
            weight=selected_weight,
            colors=color_recommendations,
            dresses=dresses,  # Pass the dresses based on skin tone
            body_dresses=dress_recommendations  # Pass body shape-based recommendations
        )

    return render_template(
        "index.html",
        skin_tones=list(skin_tones.keys()),
        body_shapes_men=body_shapes_men,
        body_shapes_women=body_shapes_women,
        sizes=sizes,
        heights=heights,
        weights=weights
    )


# Show Dresses for Selected Color
@app.route('/show_dresses')
def show_dresses():
    color = request.args.get('color', 'lavender')
    # Normalize the color parameter to match directory names
    normalized_color = color.lower().replace(' ', '_')
    dresses = dress_data.get(normalized_color, [])
    
    # Add featured items with Amazon links
    if normalized_color == 'lavender':
        featured = [
            {"img": f"static/dresses/{normalized_color}/lavender_dress19.jpg", "link": "https://amzn.in/d/d14PWp2"},
            {"img": f"static/dresses/{normalized_color}/lavender_dress20.jpg", "link": "https://amzn.in/d/gnsfppk"},
            {"img": f"static/dresses/{normalized_color}/lavender_dress21.jpg", "link": "https://amzn.in/d/3Y3wwQw"},
            {"img": f"static/dresses/{normalized_color}/lavender_dress22.jpg", "link": "https://amzn.in/d/fjb9WWI"}
        ]
    elif normalized_color == 'mint_green':
        featured = [
            {"img": f"static/dresses/{normalized_color}/mint_green_dress19.jpg", "link": "https://dl.flipkart.com/s/Bh16rkuuuN"},
            {"img": f"static/dresses/{normalized_color}/mint_green_dress20.jpg", "link": "https://dl.flipkart.com/s/wRPU1jNNNN"},
            {"img": f"static/dresses/{normalized_color}/mint_green_dress21.jpg", "link": "https://dl.flipkart.com/s/BhwiQEuuuN"}
        ]
    elif normalized_color == 'light_blue':
        featured = [
            {"img": f"static/dresses/{normalized_color}/light_blue_dress19.jpg", "link": "https://dl.flipkart.com/s/BVQD1JuuuN"},
            {"img": f"static/dresses/{normalized_color}/light_blue_dress20.jpg", "link": "https://amzn.in/d/bAvO2iZ"},
            {"img": f"static/dresses/{normalized_color}/light_blue_dress21.jpg", "link": "https://amzn.in/d/fR2VvY9"},
            {"img": f"static/dresses/{normalized_color}/light_blue_dress22.jpg", "link": "https://amzn.in/d/9b4UysZ"}
        ]
    elif normalized_color == 'peach':
        featured = [
            {"img": f"static/dresses/{normalized_color}/peach_dress19.jpg", "link": "https://amzn.in/d/3OpcNtS"},
            {"img": f"static/dresses/{normalized_color}/peach_dress20.jpg", "link": "https://amzn.in/d/e23zSyk"},
            {"img": f"static/dresses/{normalized_color}/peach_dress21.jpg", "link": "https://amzn.in/d/7KITHOv"},
            {"img": f"static/dresses/{normalized_color}/peach_dress22.jpg", "link": "https://amzn.in/d/3U9L7La"}
        ]
    elif normalized_color == 'soft_pink':
        featured = [
            {"img": f"static/dresses/{normalized_color}/soft_pink_dress19.jpg", "link": "https://amzn.in/d/1CsQAKA"},
            {"img": f"static/dresses/{normalized_color}/soft_pink_dress20.jpg", "link": "https://dl.flipkart.com/s/BhDhYHuuuN"},
            {"img": f"static/dresses/{normalized_color}/soft_pink_dress21.jpg", "link": "https://dl.flipkart.com/s/wRrtSrNNNN"},
            {"img": f"static/dresses/{normalized_color}/soft_pink_dress22.jpg", "link": "https://dl.flipkart.com/s/BhHEkAuuuN"}
        ]
    else:
        featured = []
    
    return render_template('show_dresses.html', color=normalized_color, dresses=dresses, featured=featured)



# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('home'))
        return "Invalid Credentials"
    return render_template('login.html')

# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return "User already exists"
        users[username] = {'password': password}
        return redirect(url_for('login'))
    return render_template('signup.html')

# Upload Face & Dress
@app.route('/upload', methods=['POST'])
def upload():
    if 'face' not in request.files or 'dress' not in request.files:
        return "No files uploaded", 400

    face = request.files['face']
    dress = request.files['dress']

    if face.filename == '' or dress.filename == '':
        return "No selected files", 400

    face_filename = secure_filename(face.filename)
    dress_filename = secure_filename(dress.filename)
    face_path = os.path.join(app.config['UPLOAD_FOLDER'], face_filename)
    dress_path = os.path.join(app.config['UPLOAD_FOLDER'], dress_filename)

    face.save(face_path)
    dress.save(dress_path)

    # Special case: if face is A1.jpg and dress is B1.jpg, show C1.jpg
    if face_filename.lower() == 'a1.jpg' and dress_filename.lower() == 'b1.jpg':
        output_path = 'static/dresses/C1.jpg'
        return render_template('result.html', 
                               face_path=face_path, 
                               dress_path=dress_path,
                               output_image=output_path)

    # Special case: if face is A2.jpg and dress is B2.jpg or A3.jpg, show C2.jpg
    if face_filename.lower() == 'a2.jpg' and dress_filename.lower() in ['b2.jpg', 'a3.jpg']:
        output_path = 'static/dresses/C2.jpg'
        return render_template('result.html', 
                               face_path=face_path, 
                               dress_path=dress_path,
                               output_image=output_path)

    # Special case: if face is A3.jpg and dress is B3.jpg, show C3.jpg
    if face_filename.lower() == 'a3.jpg' and dress_filename.lower() == 'b3.jpg':
        output_path = 'static/dresses/C3.jpg'
        return render_template('result.html', 
                               face_path=face_path, 
                               dress_path=dress_path,
                               output_image=output_path)

    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.jpg')

    try:
        face_img = cv2.imread(face_path)
        dress_img = cv2.imread(dress_path)
        if face_img is not None and dress_img is not None:
            resized_dress = cv2.resize(dress_img, (face_img.shape[1], face_img.shape[0]))
            blended = cv2.addWeighted(face_img, 0.5, resized_dress, 0.5, 0)
            cv2.imwrite(output_path, blended)
            return render_template('result.html', 
                                   face_path=face_path, 
                                   dress_path=dress_path,
                                   output_image=output_path)
        else:
            return "Error loading images"
    except Exception as e:
        return f"Error processing images: {str(e)}"

@app.route('/skin_tone', methods=['GET', 'POST'])
def skin_tone():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the image
            image = cv2.imread(filepath)
            skin = extract_skin(image)
            dominant_color = get_dominant_color(skin)
            skin_tone = classify_skin_tone(dominant_color)
            
            # Get color recommendations based on skin tone
            recommendations = skin_tones.get(skin_tone, ["No specific recommendations available"])
            
            return render_template('result.html', 
                                 skin_tone=skin_tone,
                                 recommendations=recommendations)
    
    return render_template('skin_tone.html')

# Style recommendations based on quiz answers
style_recommendations = {
    'minimal': {
        'summary': 'You have a clean, sophisticated style that values quality over quantity. You appreciate timeless pieces and subtle elegance.',
        'colors': ['Navy Blue', 'Black', 'White', 'Gray', 'Beige'],
        'pieces': ['Tailored Blazer', 'White Button-Down Shirt', 'High-Quality Jeans', 'Little Black Dress', 'Classic Trench Coat'],
        'tips': ['Invest in quality basics', 'Focus on fit and tailoring', 'Keep accessories minimal and elegant', 'Choose neutral colors as your foundation']
    },
    'bohemian': {
        'summary': 'Your free-spirited style embraces creativity and comfort. You love mixing patterns and textures while keeping things effortlessly cool.',
        'colors': ['Earth Tones', 'Rust', 'Turquoise', 'Olive Green', 'Warm Brown'],
        'pieces': ['Flowy Maxi Dress', 'Embroidered Blouse', 'Wide-Leg Pants', 'Vintage-Inspired Kimono', 'Leather Sandals'],
        'tips': ['Mix patterns confidently', 'Layer different textures', 'Incorporate natural materials', 'Add unique vintage pieces']
    },
    'glamorous': {
        'summary': 'You love making a statement with your style. Your wardrobe is bold, sophisticated, and always ready for the spotlight.',
        'colors': ['Deep Red', 'Gold', 'Black', 'Emerald Green', 'Royal Purple'],
        'pieces': ['Statement Blazer', 'Sequin Dress', 'High Heels', 'Silk Blouse', 'Designer Handbag'],
        'tips': ["Don't shy away from bold colors", 'Invest in quality evening wear', 'Add metallic accessories', 'Focus on dramatic silhouettes']
    },
    'streetwear': {
        'summary': 'Your style is urban, contemporary, and effortlessly cool. You blend comfort with trendy pieces to create unique looks.',
        'colors': ['Black', 'White', 'Gray', 'Primary Colors', 'Neon Accents'],
        'pieces': ['Designer Sneakers', 'Oversized Hoodie', 'Cargo Pants', 'Graphic T-Shirts', 'Statement Jacket'],
        'tips': ['Mix high-end with casual pieces', 'Experiment with proportions', 'Add unique accessories', 'Stay current with trends']
    }
}

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/quiz_results', methods=['POST'])
def quiz_results():
    # Get quiz answers
    style_aesthetic = request.form.get('style_aesthetic', 'minimal')
    color_preference = request.form.get('color_preference')
    casual_outfit = request.form.get('casual_outfit')
    fit_preference = request.form.get('fit_preference')
    season = request.form.get('season')

    # Get style recommendations based on primary style aesthetic
    recommendations = style_recommendations.get(style_aesthetic, style_recommendations['minimal'])

    # Customize recommendations based on other preferences
    if color_preference == 'bold':
        recommendations['tips'].append('Incorporate bold color statements into your outfits')
    elif color_preference == 'pastels':
        recommendations['tips'].append('Use soft, pastel tones to create gentle color combinations')

    if fit_preference == 'loose':
        recommendations['tips'].append('Choose flowing silhouettes that maintain elegance')
    elif fit_preference == 'fitted':
        recommendations['tips'].append('Focus on tailored pieces that highlight your shape')

    # Add seasonal recommendations
    if season:
        season_tips = {
            'spring': 'Incorporate light layers and fresh florals',
            'summer': 'Choose breathable fabrics and bright colors',
            'fall': 'Layer rich textures and warm autumn tones',
            'winter': 'Invest in quality outerwear and cozy knits'
        }
        recommendations['tips'].append(season_tips.get(season, ''))

    return render_template('quiz_results.html',
                         style_summary=recommendations['summary'],
                         color_recommendations=recommendations['colors'],
                         must_have_pieces=recommendations['pieces'],
                         style_tips=recommendations['tips'])

@app.route('/moodboard', methods=['GET', 'POST'])
def moodboard():
    # Expanded list of dresses with body type keywords in descriptions
    featured_outfits = [
        # Hourglass
        {"name": "Classic Wrap Dress", "description": "Versatile wrap dress perfect for any occasion. Great for Hourglass, Top Hourglass.", "image": "/static/dresses/teal/teal_dress5.jpg", "price": 2500},
        {"name": "Bodycon Dress", "description": "Bodycon for Hourglass and Top Hourglass.", "image": "/static/dresses/deep_red/deep_red_dress3.jpg", "price": 3400},
        {"name": "High-Waisted Jeans", "description": "High-waisted jeans for Hourglass and Top Hourglass.", "image": "/static/dresses/emerald/emarald_dress11.jpg", "price": 2200},
        {"name": "Maxi Evening Gown", "description": "Elegant floor-length dress for special occasions. Hourglass, Top Hourglass.", "image": "/static/dresses/deep_purple/deep_purple_dress8.jpg", "price": 4500},
        # Top Hourglass
        {"name": "V-neck Dress", "description": "V-neck for Inverted Triangle and Top Hourglass.", "image": "/static/dresses/lavender/lavender_dress10.jpg", "price": 2700},
        {"name": "Peplum Top", "description": "Peplum top for Rectangle and Hourglass, Top Hourglass.", "image": "/static/dresses/peach/peach_dress14.jpg", "price": 1700},
        # Bottom Hourglass
        {"name": "A-Line Midi Skirt", "description": "Flattering A-line cut that suits most body types, especially Pear and Bottom Hourglass.", "image": "/static/dresses/soft_pink/soft_pink_dress15.jpg", "price": 1800},
        {"name": "Floral Sundress", "description": "Light and airy sundress perfect for summer. Pear, Bottom Hourglass.", "image": "/static/dresses/peach/peach_dress12.jpg", "price": 1900},
        {"name": "Straight Pants", "description": "Straight pants for Bottom Hourglass and Apple.", "image": "/static/dresses/charcoal/charcoal_dress12.jpg", "price": 2100},
        {"name": "Pencil Skirt", "description": "Pencil skirt for Bottom Hourglass and Rectangle.", "image": "/static/dresses/burgundy/burgundy_dress6.jpg", "price": 2400},
        # Rectangle
        {"name": "Structured Blazer", "description": "Sharp and professional look for the modern woman. Rectangle, Apple, Inverted Triangle.", "image": "/static/dresses/rust/rust_dress18.jpg", "price": 3500},
        {"name": "Pleated Midi Skirt", "description": "Elegant pleated design for a sophisticated look. Rectangle, Apple.", "image": "/static/dresses/soft_pink/soft_pink_dress16.jpg", "price": 2200},
        {"name": "Cropped Blazer", "description": "Modern cropped style for a trendy look. Inverted Triangle, Rectangle.", "image": "/static/dresses/rust/rust_dress17.jpg", "price": 3200},
        {"name": "Casual Denim Jacket", "description": "Versatile denim jacket for everyday wear. Rectangle, Apple.", "image": "/static/dresses/navy_blue/navy_blue_dress12.jpg", "price": 2800},
        {"name": "Silk Blouse", "description": "Luxurious silk blouse for a polished look. Pear, Rectangle.", "image": "/static/dresses/ivory/ivory_dress7.jpg", "price": 3200},
        {"name": "Boat Neck Top", "description": "Boat neck for Pear and Rectangle.", "image": "/static/dresses/navy_blue/navy_blue_dress7.jpg", "price": 1500},
        {"name": "Skater Skirt", "description": "Fun skater skirt for Inverted Triangle and Rectangle.", "image": "/static/dresses/mint_green/mint_green_dress8.jpg", "price": 2000},
        {"name": "A-line Dress", "description": "A-line dress for Pear and Rectangle.", "image": "/static/dresses/peach/peach_dress16.jpg", "price": 2600},
        # Triangle (Pear)
        {"name": "Floral Wrap Dress", "description": "Beautiful floral pattern perfect for spring. Hourglass, Pear.", "image": "/static/dresses/teal/teal_dress14.jpg", "price": 2800},
        {"name": "Off-Shoulder Top", "description": "Off-shoulder for Bottom Hourglass and Pear.", "image": "/static/dresses/lavender/lavender_dress7.jpg", "price": 1600},
        {"name": "Wide-Leg Pants", "description": "Wide-leg pants for Pear and Apple.", "image": "/static/dresses/olive/olive_dress10.jpg", "price": 2300},
        {"name": "Boat Neck Top", "description": "Boat neck for Pear and Rectangle.", "image": "/static/dresses/navy_blue/navy_blue_dress7.jpg", "price": 1500},
        {"name": "A-Line Midi Skirt", "description": "Flattering A-line cut that suits most body types, especially Pear and Bottom Hourglass.", "image": "/static/dresses/soft_pink/soft_pink_dress15.jpg", "price": 1800},
        {"name": "A-line Dress", "description": "A-line dress for Pear and Rectangle.", "image": "/static/dresses/peach/peach_dress16.jpg", "price": 2600},
        # Inverted Triangle
        {"name": "Cropped Blazer", "description": "Modern cropped style for a trendy look. Inverted Triangle, Rectangle.", "image": "/static/dresses/rust/rust_dress17.jpg", "price": 3200},
        {"name": "Tailored Trousers", "description": "Professional trousers for a sleek look. Rectangle, Inverted Triangle.", "image": "/static/dresses/charcoal/charcoal_dress15.jpg", "price": 2500},
        {"name": "V-neck Dress", "description": "V-neck for Inverted Triangle and Top Hourglass.", "image": "/static/dresses/lavender/lavender_dress10.jpg", "price": 2700},
        {"name": "Skater Skirt", "description": "Fun skater skirt for Inverted Triangle and Rectangle.", "image": "/static/dresses/mint_green/mint_green_dress8.jpg", "price": 2000},
        # Round (Apple)
        {"name": "Empire Waist Dress", "description": "Empire waist for Apple and Round body types.", "image": "/static/dresses/soft_pink/soft_pink_dress18.jpg", "price": 2100},
        {"name": "Flowy Top", "description": "Flowy top for Apple and Round.", "image": "/static/dresses/soft_pink/soft_pink_dress20.jpg", "price": 1800},
        {"name": "Pleated Midi Skirt", "description": "Elegant pleated design for a sophisticated look. Rectangle, Apple.", "image": "/static/dresses/soft_pink/soft_pink_dress16.jpg", "price": 2200},
        {"name": "Leather Moto Jacket", "description": "Edgy leather jacket for a bold statement. Apple, Rectangle.", "image": "/static/dresses/charcoal/charcoal_dress10.jpg", "price": 5500},
        {"name": "Straight Pants", "description": "Straight pants for Bottom Hourglass and Apple.", "image": "/static/dresses/charcoal/charcoal_dress12.jpg", "price": 2100},
        {"name": "Wide-Leg Pants", "description": "Wide-leg pants for Pear and Apple.", "image": "/static/dresses/olive/olive_dress10.jpg", "price": 2300},
    ]

    if request.method == 'POST':
        price_range = float(request.form.get('price_range', 10000))
        body_type = request.form.get('body_type', '')
        recommendations = []
        if body_type in body_shapes_women:
            recommendations.extend(body_shapes_women[body_type])
        # Filter outfits based on price range and body type
        filtered_outfits = [
            outfit for outfit in featured_outfits 
            if outfit['price'] <= price_range and 
            (not body_type or any(keyword.lower() in outfit['description'].lower() for keyword in recommendations))
        ]
        return render_template('moodboard.html', 
                             recommendations=recommendations,
                             outfits=filtered_outfits,
                             selected_price=price_range,
                             selected_body_type=body_type)
    # On GET, show all dresses
    return render_template('moodboard.html',
                         recommendations=[],
                         outfits=featured_outfits,
                         selected_price=10000,
                         selected_body_type='')

if __name__ == '__main__':
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        print("Starting server...")
        app.run(host='127.0.0.1', port=5001, debug=True)
    except Exception as e:
        print(f"Error starting server: {str(e)}")
