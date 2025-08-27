# weather_recommendation.py

def get_weather_outfit(weather):
    outfits = {
        "summer": ["Cotton T-shirt", "Linen Shorts", "Sunglasses", "Sandals"],
        "winter": ["Wool Sweater", "Thermal Jacket", "Gloves", "Boots"],
        "rainy": ["Waterproof Jacket", "Gumboots", "Umbrella"],
        "spring": ["Light Cardigan", "Jeans", "Sneakers"],
        "autumn": ["Denim Jacket", "Full-sleeve Shirt", "Loafers"]
    }
    return outfits.get(weather.lower(), ["No specific outfit found"])

# occasion_styling.py

def get_occasion_outfit(occasion):
    outfits = {
        "casual": ["Jeans", "T-shirt", "Sneakers"],
        "formal": ["Suit", "Tie", "Oxford Shoes"],
        "wedding": ["Sherwani", "Saree", "Embroidered Suit"],
        "party": ["Sequin Dress", "Leather Jacket", "Boots"],
        "sports": ["Athletic Wear", "Running Shoes", "Cap"]
    }
    return outfits.get(occasion.lower(), ["No specific outfit found"])

# fabric_matching.py

def get_fabric_recommendation(comfort_level):
    fabrics = {
        "high": ["Cotton", "Linen", "Bamboo Fabric"],
        "medium": ["Denim", "Rayon", "Chiffon"],
        "low": ["Polyester", "Nylon", "Leather"]
    }
    return fabrics.get(comfort_level.lower(), ["No fabric recommendation found"])

if __name__ == "__main__":
    print("Weather-based recommendation:", get_weather_outfit("summer"))
    print("Occasion-based styling:", get_occasion_outfit("formal"))
    print("Fabric matching suggestion:", get_fabric_recommendation("high"))
