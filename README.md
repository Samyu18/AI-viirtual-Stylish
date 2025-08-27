# Fashion-Portal# AI-viirtual-Stylish
# 👗 AI Virtual Stylist

The **AI Virtual Stylist** is an intelligent fashion assistant that helps users discover and visualize outfits tailored to their **skin tone, mood, and personal style**.  
Currently under development, the project supports limited **2D outfit previews** on trained data and provides **personalized fashion recommendations**.

---

## ✨ Features (Work in Progress)

- 🎨 **Skin Tone Detection**  
  Detects user’s skin tone from uploaded photos to suggest matching outfits.

- 👕 **2D Outfit Preview**  
  Users can upload an image and visualize a dress overlay.  
  _(Currently works for a few pre-trained sample outfits only.)_

- 🧩 **Style Quiz**  
  Fun quiz that captures preferences (casual, chic, formal, etc.) and generates outfit recommendations.

- 📌 **Mood Board**  
  Create mood boards with curated inspirations.

- 🤖 **Personalized Suggestions**  
  AI-based recommendations combining quiz answers, skin tone, and mood.

---

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS (soft pastel theme with animations)  
- **Backend**: Flask (Python)  
- **AI/ML**:  
  - OpenCV for 2D try-on & image processing  
  - Custom models for skin tone detection + recommendations  
- **Database**: SQLite for storing user profiles & quiz results  

---

## 🚧 Current Limitations

- Works only on a **few pre-trained outfits** for now.  
- 2D preview not optimized for all body shapes/sizes.  
- Mood board and quiz features are experimental.  
- UI/UX still being improved.  

---

## 📌 Roadmap

- [ ] Expand outfit dataset for 2D previews  
- [ ] Add **3D try-on** support  
- [ ] Improve skin tone detection accuracy  
- [ ] Seasonal & trending outfit recommendations  
- [ ] Full deployment on Render / GitHub Pages  

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+  
- Flask  
- OpenCV  

### Installation
```bash
git clone https://github.com/Samyu18/AI-viirtual-Stylish.git
cd AI-viirtual-Stylish
pip install -r requirements.txt
