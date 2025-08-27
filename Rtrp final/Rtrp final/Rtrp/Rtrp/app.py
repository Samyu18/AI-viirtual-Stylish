from flask import Flask, render_template, request, send_from_directory
import os

app = Flask(__name__)

# Skin tone and color recommendations (with color names)
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

# Sample data for dresses (Replace with actual images)
dress_data = {
    "soft_pink": ["soft_pink_dress1.jpg", "soft_pink_dress2.jpg","soft_pink_dress3.jpg","soft_pink_dress4.jpg", "soft_pink_dress5.jpg","soft_pink_dress6.jpg",
                  "soft_pink_dress7.jpg", "soft_pink_dress8.jpg","soft_pink_dress9.jpg","soft_pink_dress10.jpg", "soft_pink_dress11.jpg","soft_pink_dress12.jpg",
                  "soft_pink_dress13.jpg", "soft_pink_dress14.jpg","soft_pink_dress15.jpg","soft_pink_dress16.jpg", "soft_pink_dress17.jpg","soft_pink_dress18.jpg","men1.jpg", "men2.jpg", "men3.jpg", "men4.jpg",
                "men5.jpg", "men6.jpg", "men7.jpg", "men8.jpg","men9.jpg", "men10.jpg", "men11.jpg", "men12.jpg"],

    "light_blue": ["light_blue_dress1.jpg", "light_blue_dress2.jpg","light_blue_dress3.jpg", "light_blue_dress4.jpg","light_blue_dress5.jpg",
                    "light_blue_dress6.jpg","light_blue_dress7.jpg", "light_blue_dress8.jpg","light_blue_dress9.jpg", "light_blue_dress10.jpg",
                    "light_blue_dress11.jpg", "light_blue_dress12.jpg","light_blue_dress13.jpg", "light_blue_dress14.jpg","light_blue_dress15.jpg",
                      "light_blue_dress16.jpg","light_blue_dress17.jpg", "light_blue_dress18.jpg","blue1.jpg", "blue2.jpg", "blue3.jpg", "blue4.jpg",
                      "blue5.jpg", "blue6.jpg", "blue7.jpg", "blue8.jpg","blue9.jpg", "blue10.jpg", "blue11.jpg", "blue12.jpg","blue13.jpg"],
    "lavender": ["lavender_dress1.jpg","lavender_dress2.jpg","lavender_dress3.jpg","lavender_dress4.jpg","lavender_dress5.jpg","lavender_dress6.jpg",
                 "lavender_dress7.jpg","lavender_dress8.jpg","lavender_dress9.jpg","lavender_dress10.jpg","lavender_dress11.jpg","lavender_dress12.jpg",
                 "lavender_dress13.jpg","lavender_dress14.jpg","lavender_dress15.jpg","lavender_dress16.jpg","lavender_dress17.jpg","lavender_dress18.jpg","men1.jpg", "men2.jpg", "men3.jpg", "men4.jpg",
                "men5.jpg", "men6.jpg", "men7.jpg", "men8.jpg","men9.jpg"],
    "peach": ["peach_dress1.jpg", "peach_dress2.jpg","peach_dress3.jpg", "peach_dress4.jpg","peach_dress5.jpg", "peach_dress6.jpg",
              "peach_dress7.jpg", "peach_dress8.jpg","peach_dress9.jpg", "peach_dress10.jpg","peach_dress11.jpg", "peach_dress12.jpg",
              "peach_dress13.jpg","peach_dress14.jpg", "peach_dress15.jpg","peach_dress16.jpg","peach_dress17.jpg", "peach_dress18.jpg","men1.jpg", "men2.jpg", "men3.jpg", "men4.jpg",
                "men5.jpg", "men6.jpg", "men7.jpg", "men8.jpg","men9.jpg","men10.jpg","men11.jpg"],

    "mint_green": ["mint_green_dress1.jpg", "mint_green_dress2.jpg","mint_green_dress3.jpg", "mint_green_dress4.jpg","mint_green_dress5.jpg", "mint_green_dress6.jpg",
                   "mint_green_dress7.jpg", "mint_green_dress8.jpg","mint_green_dress9.jpg", "mint_green_dress10.jpg","mint_green_dress11.jpg", "mint_green_dress12.jpg",
                   "mint_green_dress13.jpg","mint_green_dress14.jpg", "mint_green_dress15.jpg","mint_green_dress16.jpg","mint_green_dress17.jpg", "mint_green_dress18.jpg",
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

@app.route("/", methods=["GET", "POST"])
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

        # Get color recommendations
        color_recommendations = skin_tones[selected_skin_tone]

        return render_template(
            "result.html",
            skin_tone=selected_skin_tone,
            gender=selected_gender,
            body_shape=selected_body_shape,
            size=selected_size,
            height=selected_height,
            weight=selected_weight,
            colors=color_recommendations,
            dresses=dress_recommendations
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

@app.route('/show_dresses')
def show_dresses():
    color = request.args.get('color')  # Fetch color from query parameters
    if not color:
        return "Error: No color provided", 400  # Handle missing color
    normalized_color = color.replace(' ', '_')
    dresses = dress_data.get(normalized_color, [])
    return render_template("dresses.html", color=normalized_color, dresses=dresses)

# Serve static images from the dresses directory
# @app.route('/static/dresses/<color>/<filename>')
# def get_dress_image(color, filename):
#     directory = os.path.join("static", "dresses", color)
#     return send_from_directory(directory, filename)

@app.route('/dress_images/<color>/<filename>')
def get_dress_image(color, filename):
    return send_from_directory(f'static/dresses/{color}', filename)
# def show_dresses(color):
#     dresses = dress_data.get(color, [])
#     print(f"Debug: {color} dresses = {dresses}")  # Print to check if images exist
#     return render_template("dresses.html", color=color, dresses=dresses)
if __name__ == "__main__":
    app.run(debug=True)
