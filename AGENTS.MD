Lovelace is an agentic shopping experience with inspiration from the game Love & Deepspace,
integrating a 3D Hot Guy Avatar as a "Virtual Boyfriend". Users are able to do the following:

1.) "video call" and comment on you / your surroundings / your clothes
2.) scan and store your wardrobe's outfits
3.) discover new clothes on shopee etc
4.) have different tastes (affinities with different kinds of clothes, etc.)
5.) be able to judge your clothing / outfits by
6.) VTO (virtual try-on) your outfits, literally putting the clothes on the user
7.) sync with your google calendar to see if there's any occasions
8.) buy stuff for you, using your payment details
9.) take photobooth photos with you
10.) recommend new clothes based on your existing ones / whatever you're searching for

## Technical Integrations

### Nano Banana (Google Gemini Image Generation)

- **Purpose**: AI-powered image generation and editing for VTO, avatars, and photobooth
- **Models**:
  - `gemini-2.5-flash-image` (Fast) - For previews and rapid iterations
  - `gemini-3-pro-image-preview` (Pro) - For high-quality final renders
- **Features**:
  - Text-to-Image generation for avatar creation
  - Image-to-Image editing for virtual try-on
  - Multi-turn iterative editing
  - Photobooth image generation
  - Product visualization
- **Documentation**: See `backend/src/NanoBanana/README.md`
- **Module**: `backend/src/NanoBanana/nano_banana.py`

### Product-to-3D Pipeline

- **Purpose**: Convert product/clothing images to 3D models for virtual try-on and AR experiences
- **Speed**: 0.5 seconds to 1 minute depending on quality level
- **Providers**:
  - Stable Fast 3D (0.5s, fastest)
  - TripoSR via Replicate (30s, best balance)
  - sudoAI (60s, simple integration)
  - SAM 3D, Instant3D, Reali3 (high quality options)
- **Features**:
  - Single image to 3D conversion
  - Background removal
  - Mesh optimization (decimation, normals)
  - Multiple quality tiers (preview/standard/high/premium)
  - Output formats: GLB, OBJ, FBX
  - REST API with async support
- **Documentation**: See `backend/src/ProductTo3DPipeline/README.md` and `QUICKSTART.md`
- **Module**: `backend/src/ProductTo3DPipeline/product_to_3d_pipeline.py`
- **API Service**: `backend/src/ProductTo3DPipeline/api.py`

our tech stack is as follows:
1.) fastapi
2.) nextjs, tailwind

DO NOT MAKE ANY MARKDOWN FILES!
