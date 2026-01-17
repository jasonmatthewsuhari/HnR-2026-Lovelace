# Windows OpenCV GUI Fix

## Problem

If you see this error:
```
cv2.error: OpenCV(4.12.0) ... The function is not implemented. 
Rebuild the library with Windows, GTK+ 2.x or Cocoa support.
```

This means your OpenCV installation doesn't have GUI support.

## Solution

### Quick Fix (Recommended)

Uninstall `opencv-python` and install `opencv-contrib-python` instead:

```powershell
# Uninstall old version
pip uninstall opencv-python -y

# Install version with GUI support
pip install opencv-contrib-python
```

Then run the photobooth again:
```powershell
python photobooth.py
```

### Verify Installation

```powershell
python -c "import cv2; print(cv2.__version__); print('OpenCV working!')"
```

Should output:
```
4.x.x
OpenCV working!
```

## Why This Happens

- `opencv-python` is a minimal build without GUI support
- `opencv-contrib-python` includes full GUI functionality
- On Windows, you need the GUI support for `cv2.imshow()` to work

## Alternative: Use Headless Mode

If you still have issues, you can use the headless capture mode (coming soon in update).

## Still Not Working?

### Option 1: Full Reinstall

```powershell
# Remove all opencv packages
pip uninstall opencv-python opencv-python-headless opencv-contrib-python -y

# Install fresh
pip install opencv-contrib-python==4.8.1.78
```

### Option 2: Check Python Version

Make sure you're using Python 3.8-3.11 (OpenCV may have issues with 3.12+):

```powershell
python --version
```

### Option 3: Install All Dependencies Fresh

```powershell
# Navigate to Photobooth folder
cd backend\src\Photobooth

# Install all requirements
pip install -r requirements.txt
```

## Test Your Setup

After fixing, run the test:

```powershell
python test_setup.py
```

Should show:
```
[4] Checking webcam...
   ✅ Webcam accessible
```

## Summary

**Quick fix:**
```powershell
pip uninstall opencv-python -y
pip install opencv-contrib-python
python photobooth.py
```

That's it! 🎉
