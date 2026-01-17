# Photobooth Module

AI-powered couple's photobooth with your virtual boyfriend avatar! Take romantic photos together with AI-generated backgrounds.

## 🚀 Quick Start

```bash
cd backend/src/Photobooth
python photobooth.py
```

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## ✨ Features

- 📸 3 romantic photobooth backgrounds (café, beach, home)
- ⏰ 5-second countdown timer
- ✂️ Automatic background removal
- 🎨 Professional couple's photos
- 💾 All photos saved automatically

## 📖 Documentation

- **[README.md](README.md)** - Complete guide and tips
- **[QUICKSTART.md](QUICKSTART.md)** - Setup and usage
- **[API.md](API.md)** - API reference for developers
- **[example_usage.py](example_usage.py)** - Code examples

## 🎯 Requirements

```bash
pip install google-genai pillow opencv-python numpy

# Optional (better background removal):
pip install rembg
```

## 📸 How It Works

1. System generates 3 romantic backgrounds with your avatar
2. For each background:
   - Webcam opens
   - Press SPACE to start countdown
   - 5... 4... 3... 2... 1... SNAP! 📸
   - Your photo is captured and composited
3. All 3 couple's photos are saved!

## 🎨 Example Output

```
photobooth_1_romantic_cafe.png   - You and avatar at a cozy café ☕
photobooth_2_sunset_beach.png    - You and avatar on the beach 🌅
photobooth_3_cozy_home.png       - You and avatar at home 🏠
```

## 🔑 Setup

1. Get API key from [ai.google.dev](https://ai.google.dev/)
2. Set environment variable:
   ```powershell
   $env:GEMINI_API_KEY='your-key-here'
   ```
3. Place `avatar.jpg` in this folder
4. Run `python photobooth.py`

## 💡 Tips for Best Photos

- ✅ Good lighting (face a window or lamp)
- ✅ Plain background (light colored wall)
- ✅ Camera at chest/face height
- ✅ Smile naturally!

## 🛠️ Testing Setup

```bash
python test_setup.py
```

This checks all dependencies, API key, avatar, and webcam.

## 📚 Developer API

```python
from photobooth import run_photobooth_session

# Run complete session
photos = run_photobooth_session(
    avatar_path="avatar.jpg",
    background_removal=True
)

print(f"Created {len(photos)} photos!")
```

See [API.md](API.md) for full API documentation.

## 🔗 Integration

This module integrates with:
- **LiveVideoCall** - Use video call avatar
- **WardrobeDB** - Show off outfits
- **Main App** - Add to UI

## ⚡ Made with

- Google Gemini AI (background generation)
- OpenCV (webcam capture)
- rembg (background removal)
- PIL (image processing)

---

**Ready for your photoshoot?** Run `python photobooth.py`! 📸✨💕
