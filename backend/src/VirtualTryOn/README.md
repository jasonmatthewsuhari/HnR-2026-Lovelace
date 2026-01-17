# Virtual Try-On Module

AI-powered virtual try-on using Google's Nano Banana (Gemini Image Generation) API.

## Features

- 🎯 Apply clothing from one image onto a person in another image
- 🤖 AI-powered analysis of clothing details
- 🎨 Photorealistic results with proper lighting and perspective
- 📸 Maintains person's pose, face, and background
- ⚡ Fast processing (10-30 seconds)

## Quick Start

### 1. Install Dependencies

```bash
pip install google-genai pillow
```

### 2. Get API Key

1. Visit [ai.google.dev](https://ai.google.dev/)
2. Sign in and create an API key
3. Set environment variable:

**Linux/Mac:**
```bash
export GEMINI_API_KEY='your-key-here'
```

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY='your-key-here'
```

### 3. Prepare Images

Place two images in `backend/src/LiveVideoCall/`:
- `person.jpg` - Photo of a person
- `clothing.jpg` - Photo of clothing item

### 4. Run Demo

```bash
cd backend/src/VirtualTryOn
python virtual_try_on.py
```

## How It Works

1. **Analyze Clothing**: AI analyzes the clothing image to extract details (color, style, type)
2. **Generate Prompt**: Creates a detailed prompt for virtual try-on
3. **Image Generation**: Uses Nano Banana to apply clothing onto person
4. **Save Result**: Outputs photorealistic result to `virtual_tryon_result.png` (same folder)

## Example Output

The demo will:
- Load both images
- Analyze the clothing
- Generate the virtual try-on
- Save result to `backend/src/VirtualTryOn/virtual_tryon_result.png`
- Automatically open the result (if possible)

## Technical Details

### API Used
- **Model**: `gemini-2.5-flash-image` (Nano Banana)
- **Analysis Model**: `gemini-2.0-flash-exp` (for clothing analysis)
- **Processing Time**: 10-30 seconds per try-on

### Image Requirements

**Person Image:**
- Clear, well-lit photo
- Person facing camera
- Full or upper body visible
- JPG or PNG format

**Clothing Image:**
- Clear view of clothing item
- Good lighting
- Can be product photo or worn by someone
- JPG or PNG format

### Output
- Format: PNG
- Location: `virtual_tryon_result.png` (same folder as the script)
- Quality: High-resolution photorealistic

## Troubleshooting

### "GEMINI_API_KEY not set"
**Solution**: Set the environment variable with your API key from ai.google.dev

### "person.jpg not found"
**Solution**: Place your person image at `backend/src/LiveVideoCall/person.jpg`

### "clothing.jpg not found"
**Solution**: Place your clothing image at `backend/src/LiveVideoCall/clothing.jpg`

### "Module not found"
**Solution**: Install dependencies: `pip install google-genai pillow`

### Poor results
**Solutions**:
- Use clear, well-lit images
- Ensure person is facing camera
- Use high-quality clothing images
- Try different clothing angles

## Advanced Usage

### Using in Your Code

```python
import os
from virtual_try_on import virtual_try_on

api_key = os.getenv('GEMINI_API_KEY')

result_path = virtual_try_on(
    person_path="path/to/person.jpg",
    clothing_path="path/to/clothing.jpg",
    api_key=api_key,
    output_dir="."  # Current directory
)

print(f"Result: {result_path}")
```

### Batch Processing

```python
import os
from pathlib import Path
from virtual_try_on import virtual_try_on

api_key = os.getenv('GEMINI_API_KEY')
person_image = "person.jpg"
clothing_dir = Path("clothing_items")

for clothing_img in clothing_dir.glob("*.jpg"):
    output_name = f"output/tryon_{clothing_img.stem}.png"
    virtual_try_on(person_image, str(clothing_img), api_key, "output")
```

## Integration with Lovelace

This module is designed to integrate with:

- **WardrobeDB**: Try on clothes from user's wardrobe
- **ClothesSearch**: Try on discovered clothing items
- **MainApp**: Provide virtual try-on in the UI

### Example: Try on from Wardrobe

```python
from WardrobeDB.wardrobe_db import WardrobeDB
from VirtualTryOn.virtual_try_on import virtual_try_on

# Get clothing item from database
db = WardrobeDB()
item = db.get_clothing_item('item_123')

# Get clothing image URL
clothing_image_url = item.images[0]

# Download and try on
# ... download logic ...
result = virtual_try_on(
    person_path="user_photo.jpg",
    clothing_path="downloaded_clothing.jpg",
    api_key=api_key
)
```

## Rate Limits

**Free Tier:**
- 15 requests/minute
- 1,500 requests/day

**Paid Tier:**
- Higher limits
- Priority processing

The demo includes automatic retry logic for rate limits.

## Cost Optimization

- Cache results for same person/clothing combinations
- Use lower resolution for previews
- Batch similar requests
- Implement user request limits

## Future Enhancements

- [ ] Multiple clothing items at once (full outfit)
- [ ] Style transfer options
- [ ] Color variations
- [ ] Size/fit adjustments
- [ ] Video try-on (frame by frame)
- [ ] AR integration
- [ ] Body type adaptation

## Support

For issues or questions:
1. Check this README
2. Verify API key is set correctly
3. Ensure images are in the correct location
4. Check error messages for specific issues

## Links

- [Google AI Studio](https://ai.google.dev/)
- [Nano Banana Documentation](https://ai.google.dev/gemini-api/docs/image-generation)
- [Lovelace Project](../../README.md)

---

**Ready to try?** Run `python virtual_try_on.py` and see the magic! ✨👗
