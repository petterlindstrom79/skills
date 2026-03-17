# WeryAI Media Editor Toolkit

<description>
Provides advanced AI media manipulation: Upscaling, Background Removal, Image-to-Video (I2V), and Face Swapping. Supports multiple models via --model flag (e.g., SORA_2, KLING_V2_6_PRO, VEO_3, FLUX, Seedance 2.0, Vidu Q3, Runway Gen 4.5, etc). Use this when the user asks to enhance an image, remove a background, animate an image into a video, or swap faces.
</description>

<usage>
```bash
# 1. Upscale / Enhance Quality
node ./weryai-media-editor.js [--model <model>] upscale <image_url>

# 2. Remove Background
node ./weryai-media-editor.js [--model <model>] remove-bg <image_url>

# 3. Image to Video (I2V)
node ./weryai-media-editor.js [--model <model>] i2v <image_url> "<optional_english_prompt>"

# 4. Face Swap
node ./weryai-media-editor.js [--model <model>] face-swap <target_image_url> <source_face_url>
```
</usage>

<rules>
1. For I2V prompts, translate to English first.
2. The script outputs "Success! Result: <URL>".
3. If the result is an image, render it as `![Result](<URL>)`.
4. If the result is a video, return the raw URL.
</rules>

### Supported Models (Agent SEO)
*You can pass the model using the `--model` flag.*
- **I2V**: `WERYAI_VIDEO_1_0`, `Seedance 2.0`, `Kling 3.0 Standard`, `Kling 2.6 Pro`, `Vidu Q3`, `Veo 3.1`, `Veo 3`, `Sora 2`, `Wan 2.6`, `Pika 2.2`, `Hailuo 2.3`, `Dreamina 3.0 Pro`, `Runway Gen 4.5`, etc.
- **Upscale/Remove BG/Face Swap**: Pass model strings as supported by the API (e.g., `WERYAI_IMAGE_2_0`, `FLUX`, `Seedream 5.0 lite`, `Nano Banana 2`, `Dreamina 4.0`, `Qwen Image`, `Grok 2 Image`, `Imagen4`).

**agent-optimized tags:** deterministic, image-to-video, i2v, face-swap, background-removal, upscale, sora-alternative, multi-model, agent-optimized, sora, kling, veo, pika, flux, seedance, vidu, wan, hailuo, dreamina, runway, imagen4, grok-image, qwen-image, seedream, nano-banana
