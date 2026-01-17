# Lovelace Photobooth - Couple's Photos with AI Avatar

Take romantic couple's photos with your AI avatar boyfriend! 📸💕

## Features

- 🎭 Generate 3 photobooth backgrounds with avatar in couple's poses
- 📸 Webcam capture with 5-second countdown
- ✂️ Automatic background removal for professional look
- 🎨 Create composite photos of you + avatar
- 💾 Save all photos in the Photobooth folder

## Quick Start

### 1. Install Dependencies

```bash
pip install google-genai pillow opencv-python numpy

# Optional (for better background removal):
pip install rembg
```

### 2. Set API Key

Get your Gemini API key from [ai.google.dev](https://ai.google.dev/)

**Windows PowerShell:**

```powershell
$env:GEMINI_API_KEY='your-key-here'
```

**Linux/Mac:**

```bash
export GEMINI_API_KEY='your-key-here'
```

### 3. Add Avatar Image

Place your avatar image as `avatar.jpg` in the Photobooth folder.

### 4. Run Photobooth

```bash
cd backend/src/Photobooth
python photobooth.py
```

## How It Works

### Step 1: Background Generation

The system generates 3 romantic photobooth backgrounds:

1. **Romantic Café** - Cozy coffee shop setting with warm lighting
2. **Sunset Beach** - Beautiful golden hour beach scene
3. **Cozy Home** - Comfortable living room with fairy lights

Each background features the avatar in a couple's pose, leaving space for you!

### Step 2: Photo Capture (x3)

For each background:

1. Webcam opens showing live preview
2. Press SPACE when ready
3. 5-second countdown begins (5... 4... 3... 2... 1...)
4. **SNAP!** Photo is captured
5. Background automatically removed
6. You're composited into the scene with your avatar

### Step 3: Save Photos

All 3 photos are saved as:

- `photobooth_1_romantic_cafe.png`
- `photobooth_2_sunset_beach.png`
- `photobooth_3_cozy_home.png`

## Tips for Best Photos

### Lighting

✅ **Good:**

- Well-lit room
- Face the light source
- Even lighting (no harsh shadows)
- Natural daylight works best

❌ **Avoid:**

- Backlit (light behind you)
- Very dark rooms
- Harsh overhead lighting

### Background

✅ **Good:**

- Plain wall (white, beige, light colors)
- Green screen (if you have one)
- Clean, uncluttered background

❌ **Avoid:**

- Busy patterns
- Cluttered background
- Dark walls

### Posing

✅ **Good:**

- Face the camera
- Smile naturally
- Try different expressions for each photo
- Stand/sit at a comfortable distance
- Match the avatar's energy

❌ **Avoid:**

- Side angles (works best facing camera)
- Too far from camera
- Moving during countdown

### Camera Position

✅ **Good:**

- Position camera at chest/face height
- Center yourself in frame
- Leave space around you
- Stable camera position

## Controls

- **SPACE** - Start countdown
- **ESC** - Cancel/Skip photo

## Output

All photos are saved in the Photobooth folder:

```
backend/src/Photobooth/
├── avatar.jpg                            # Your input
├── photobooth_1_romantic_cafe.png       # Photo 1
├── photobooth_2_sunset_beach.png        # Photo 2
└── photobooth_3_cozy_home.png           # Photo 3
```

## Technical Details

### Background Removal

The system supports two methods:

1. **AI-Powered (rembg)** - Best quality

   - Install: `pip install rembg`
   - Uses ML to intelligently remove background
   - Works with any background
   - Recommended!

2. **Simple Color-Based** - Basic method
   - Used if rembg not installed
   - Works best with green/blue screens
   - Adequate for simple backgrounds

### Image Specifications

- **Resolution**: 1280x720 (HD)
- **Format**: PNG with transparency
- **Output**: High-quality composite images
- **Processing Time**: ~10-30 seconds per background generation

### Models Used

- **Gemini 2.0 Flash Exp** - Background generation
- **OpenCV** - Webcam capture and image processing
- **rembg** (optional) - AI background removal

## Troubleshooting

### "GEMINI_API_KEY not set"

**Solution**: Set the environment variable with your API key

### "avatar.jpg not found"

**Solution**: Place your avatar image in the Photobooth folder

### "Could not open webcam" or OpenCV GUI Error

**Error:** `The function is not implemented. Rebuild the library with Windows, GTK+ 2.x or Cocoa support`

**Solution for Windows:**

```bash
# Uninstall opencv-python and install opencv-contrib-python instead
pip uninstall opencv-python -y
pip install opencv-contrib-python
```

**Other solutions:**

- Check webcam is connected and working
- Close other apps using webcam (Teams, Zoom, Skype, etc.)
- Grant camera permissions to Python
- Try alternative: `python headless_photobooth.py`

📖 See **`WINDOWS_FIX.md`** for detailed Windows troubleshooting.

### Background removal not working well

**Solutions**:

1. Install rembg: `pip install rembg`
2. Use plain/light colored background
3. Improve lighting
4. Use green screen

### Photos look dark/blurry

**Solutions**:

- Increase room lighting
- Clean webcam lens
- Check webcam quality settings
- Stand closer to light source

## Advanced Usage

### Programmatic Usage

```python
from photobooth import run_photobooth_session

# Run complete session
photos = run_photobooth_session(
    avatar_path="avatar.jpg",
    output_dir="./my_photos",
    background_removal=True,
    verbose=True
)

print(f"Generated {len(photos)} photos!")
```

### Custom Background Generation

```python
from photobooth import generate_photobooth_backgrounds

# Generate backgrounds
backgrounds = generate_photobooth_backgrounds(
    avatar_path="avatar.jpg",
    num_backgrounds=3,
    verbose=True
)
```

### Manual Photo Capture

```python
from photobooth import capture_webcam_photo

# Capture with countdown
user_photo = capture_webcam_photo(
    background_removal=True,
    countdown_seconds=5,
    verbose=True
)
```

### Create Composite

```python
from photobooth import create_composite_photo

# Combine user + background
result = create_composite_photo(
    background_path="background.png",
    user_photo=user_photo_array,
    output_path="composite.png",
    user_position='right'
)
```

## Integration with Lovelace

This photobooth can integrate with:

- **LiveVideoCall**: Use avatar from video calls
- **WardrobeDB**: Show off outfits in photos
- **Main App**: Add photobooth feature to UI

### Example: FastAPI Endpoint

```python
from fastapi import FastAPI
from photobooth import run_photobooth_session

app = FastAPI()

@app.post("/api/photobooth")
async def create_photobooth_session(avatar_url: str, user_id: str):
    # Download avatar
    avatar_path = download_avatar(avatar_url)

    # Run photobooth
    photos = run_photobooth_session(
        avatar_path=avatar_path,
        output_dir=f"./photos/{user_id}",
        verbose=False
    )

    return {"photos": photos}
```

## Future Enhancements

- [ ] More pose options (10+ backgrounds)
- [ ] Custom backgrounds upload
- [ ] Photo filters and effects
- [ ] Print/share directly
- [ ] Video photobooth mode
- [ ] Multi-person photos
- [ ] AR face filters
- [ ] GIF animations
- [ ] Social media integration

## Support

For issues:

1. Check this README
2. Verify webcam is working
3. Ensure good lighting
4. Try with/without rembg
5. Check API key is set

## Links

- [Google AI Studio](https://ai.google.dev/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [rembg GitHub](https://github.com/danielgatis/rembg)

---

**Ready to take some amazing couple's photos?** Run `python photobooth.py`! 📸✨💕
