# NemoEdit API Reference

**Base URL:** `https://mega-api-dev.nemovideo.ai`

All requests require:
```
Authorization: Bearer <NEMOVIDEO_API_KEY>
Content-Type: application/json
```

---

## 1. Upload Media

```http
POST /v1/upload
Content-Type: multipart/form-data

file=<binary>
```

**Response:**
```json
{
  "file_id": "f_abc123",
  "filename": "interview_raw.mp4",
  "duration_seconds": 342,
  "width": 1920,
  "height": 1080,
  "fps": 29.97,
  "has_audio": true,
  "size_bytes": 890000000
}
```

Upload each clip, music track, image, and LUT file separately. Use `file_id` in all subsequent requests.

**Limits:** 4GB per file, 8 hours max source duration.

---

## 2. Create Edit Job (Timeline)

```http
POST /v1/edit
Content-Type: application/json
```

**Request body:**
```json
{
  "timeline": [
    {
      "file_id": "f_abc123",
      "trim": { "start": 5.2, "end": 42.0 },
      "speed": 1.0,
      "audio": { "volume": 1.0, "denoise": false }
    },
    {
      "file_id": "f_def456",
      "trim": { "start": 0.0, "end": 28.5 },
      "transition_in": { "type": "cross_dissolve", "duration": 0.5 },
      "speed": 1.0
    }
  ],
  "audio_tracks": [
    {
      "file_id": "f_bgm789",
      "type": "bgm",
      "volume": 0.3,
      "duck_under_voice": true,
      "fade_in": 1.0,
      "fade_out": 2.0
    }
  ],
  "color": {
    "preset": "cinematic_warm",
    "brightness": 0.05,
    "contrast": 0.1,
    "saturation": 0.05,
    "temperature": 200
  },
  "output": {
    "format": "mp4",
    "codec": "h264",
    "resolution": "1920x1080",
    "fps": 29.97,
    "preset": "youtube"
  }
}
```

**Response:**
```json
{
  "job_id": "job_edit_abc001",
  "status": "queued",
  "timeline_duration_seconds": 68.5,
  "estimated_seconds": 180
}
```

---

### Timeline Clip Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file_id` | string | ✅ | Uploaded clip file ID |
| `trim.start` | float | ❌ | Clip start time in seconds (default: 0) |
| `trim.end` | float | ❌ | Clip end time in seconds (default: full length) |
| `speed` | float | ❌ | Playback speed multiplier (0.1–10.0, default: 1.0) |
| `speed_ramp` | object | ❌ | Speed ramp keyframes (see Speed Ramp section) |
| `transition_in` | object | ❌ | Transition from previous clip into this one |
| `transition_out` | object | ❌ | Transition from this clip out to next |
| `audio.volume` | float | ❌ | Clip audio volume (0.0–2.0, default: 1.0) |
| `audio.denoise` | bool | ❌ | Apply AI audio denoising (default: false) |
| `audio.normalize` | bool | ❌ | Normalize audio levels (default: false) |
| `audio.mute` | bool | ❌ | Mute this clip's audio (default: false) |
| `color` | object | ❌ | Per-clip color override (overrides global color) |
| `background` | object | ❌ | Background removal/replacement |
| `pip` | object | ❌ | Picture-in-picture overlay |

---

### Transition Types

| `type` | Description |
|--------|-------------|
| `cut` | Hard cut (default, no transition) |
| `cross_dissolve` | Smooth cross-fade between clips |
| `dip_black` | Dip to black then fade up |
| `dip_white` | Dip to white then fade up |
| `wipe_left` | Horizontal wipe left-to-right |
| `wipe_right` | Horizontal wipe right-to-left |
| `zoom_push` | Zoom-punch cut (energetic) |
| `slide_left` | Slide next clip in from right |
| `slide_right` | Slide next clip in from left |

Transition `duration` in seconds (default: 0.5, max: 3.0).

---

### Speed Ramp

```json
"speed_ramp": {
  "keyframes": [
    { "time": 0.0, "speed": 1.0 },
    { "time": 2.0, "speed": 0.3 },
    { "time": 4.0, "speed": 0.3 },
    { "time": 5.5, "speed": 1.0 }
  ],
  "interpolation": "smooth"
}
```

| Field | Values | Description |
|-------|--------|-------------|
| `keyframes[].time` | float | Time offset within the clip (seconds) |
| `keyframes[].speed` | float (0.05–10.0) | Speed at that keyframe |
| `interpolation` | `"smooth"` / `"linear"` | Ramp curve type (default: smooth) |

> For smooth slow-motion, source clip should be 60fps or higher. Warn user if source FPS ≤ 30.

---

### Color Grading

```json
"color": {
  "preset": "cinematic_warm",
  "lut_file_id": "f_lut001",
  "brightness": 0.0,
  "contrast": 0.0,
  "saturation": 0.0,
  "temperature": 0,
  "tint": 0,
  "highlights": 0.0,
  "shadows": 0.0,
  "whites": 0.0,
  "blacks": 0.0
}
```

Can be set globally (all clips) or per-clip. Numeric range: `-1.0` to `+1.0`; `temperature`/`tint`: `-500` to `+500`.

**Color presets:**

| Preset | Look |
|--------|------|
| `none` | No grade (default) |
| `cinematic_warm` | Warm golden-hour, slightly desaturated |
| `cinematic_cool` | Blue-teal shadows, clean highlights |
| `flat_log` | Flat/log-like for further grading |
| `vivid` | High saturation, punchy colors |
| `bw` | Black and white conversion |
| `vintage_film` | Film grain + faded look |
| `documentary` | Natural, slightly cool, high contrast |

**LUT:** Upload `.cube` file via `/v1/upload`, pass `file_id` as `lut_file_id`. Max 65-point resolution.

---

### Background Removal / Replacement

```json
"background": {
  "mode": "remove",
  "replacement": { "type": "color", "color": "#1a1a2e" }
}
```

```json
"background": {
  "mode": "remove",
  "replacement": { "type": "image", "file_id": "f_bg_img001" }
}
```

```json
"background": {
  "mode": "blur",
  "blur_amount": 25
}
```

| `mode` | Description |
|--------|-------------|
| `remove` | AI foreground/background segmentation (any background) |
| `chroma_key` | Green/blue screen chroma key (add `"chroma_color": "#00FF00"`) |
| `blur` | Keep background, apply gaussian blur |

> Works best with stationary camera. For handheld/fast motion, `blur` mode is more stable.

---

### Picture-in-Picture (PiP)

```json
"pip": {
  "file_id": "f_secondary_clip",
  "position": "bottom_right",
  "size": 0.25,
  "border_radius": 8,
  "border_color": "#FFFFFF",
  "border_width": 2,
  "start_at": 0.0,
  "end_at": null
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `position` | `"bottom_right"` | `top_left`, `top_right`, `bottom_left`, `bottom_right`, `center` |
| `size` | `0.25` | PiP size as fraction of main frame (0.1–0.9) |
| `border_radius` | `0` | Corner rounding in pixels |
| `border_color` | `null` | Border hex color |
| `border_width` | `0` | Border width in pixels |
| `start_at` | `0.0` | When PiP appears (seconds) |
| `end_at` | `null` | When PiP disappears (null = entire clip) |

---

### Audio Tracks

```json
"audio_tracks": [
  {
    "file_id": "f_bgm789",
    "type": "bgm",
    "volume": 0.25,
    "duck_under_voice": true,
    "duck_level": 0.15,
    "fade_in": 1.0,
    "fade_out": 2.5,
    "loop": false
  },
  {
    "file_id": "f_voiceover_001",
    "type": "voiceover",
    "volume": 1.0,
    "denoise": true,
    "normalize": true,
    "start_at": 3.0
  }
]
```

| Field | Description |
|-------|-------------|
| `type` | `bgm`, `voiceover`, `sfx` |
| `volume` | Track volume (0.0–2.0) |
| `duck_under_voice` | Auto-reduce BGM when voice detected |
| `duck_level` | Volume during ducking (default: 0.15) |
| `fade_in` / `fade_out` | Fade duration in seconds |
| `loop` | Loop audio if shorter than video (default: false) |
| `start_at` | Delay track start by N seconds |
| `denoise` | AI denoising |
| `normalize` | Normalize loudness to -14 LUFS |

---

### Output Settings

```json
"output": {
  "format": "mp4",
  "codec": "h264",
  "resolution": "1920x1080",
  "fps": 29.97,
  "bitrate_kbps": 8000,
  "preset": "youtube",
  "audio_codec": "aac",
  "audio_bitrate_kbps": 192
}
```

**Presets:**

| Preset | Format | Codec | Resolution | Notes |
|--------|--------|-------|------------|-------|
| `youtube` | MP4 | H.264 | source | 16Mbps, 2-pass |
| `youtube_4k` | MP4 | H.265 | 3840×2160 | 35Mbps |
| `instagram` | MP4 | H.264 | 1080×1080 | Square crop |
| `vimeo` | MP4 | H.264 | source | High-quality |
| `web` | WebM | VP9 | source | Web-optimized |
| `prores` | MOV | ProRes 422 | source | Post-production |
| `archive` | MP4 | H.265 | source | Max quality |

---

## 3. Add Titles and Motion Graphics

```http
POST /v1/edit/{job_id}/titles
Content-Type: application/json
```

```json
{
  "titles": [
    {
      "text": "Chapter 1: The Beginning",
      "style": "lower_third",
      "start_at": 2.0,
      "duration": 4.0,
      "position": "bottom_left",
      "font": "Montserrat",
      "font_size": 36,
      "color": "#FFFFFF",
      "animation_in": "slide_up",
      "animation_out": "fade"
    }
  ]
}
```

**Styles:** `title`, `lower_third`, `lower_third_sub`, `chapter_marker`, `end_card`, `caption`

**Animations:** `fade`, `slide_up`, `slide_left`, `zoom_in`, `typewriter`, `none`

**Fonts:** `Arial`, `Montserrat`, `Roboto`, `Helvetica`, `Georgia`, `Impact`, `Open Sans`, `Playfair Display`

---

## 4. Cut Operations

```http
POST /v1/edit/{job_id}/cuts
Content-Type: application/json
```

```json
{
  "operations": [
    { "type": "j_cut", "clip_index": 1, "audio_lead_seconds": 1.5 },
    { "type": "l_cut", "clip_index": 2, "audio_trail_seconds": 1.0 },
    { "type": "insert", "after_clip_index": 1, "file_id": "f_broll_001", "trim": { "start": 0, "end": 3.0 } },
    { "type": "remove", "clip_index": 3 }
  ]
}
```

| Type | Description |
|------|-------------|
| `j_cut` | Audio from next clip starts before video cut |
| `l_cut` | Audio from current clip continues after video cut |
| `insert` | Insert B-roll clip at a position |
| `remove` | Remove a clip from the timeline |
| `reorder` | Change clip position (`from_index`, `to_index`) |
| `split` | Split clip at time T (`clip_index`, `split_at_seconds`) |

---

## 5. Split Screen Layout

```http
POST /v1/edit/split-screen
Content-Type: application/json
```

```json
{
  "layout": "side_by_side",
  "clips": [
    { "file_id": "f_clip_left", "trim": { "start": 10.0, "end": 45.0 }, "audio": { "volume": 1.0 } },
    { "file_id": "f_clip_right", "trim": { "start": 0.0, "end": 35.0 }, "audio": { "volume": 0.0 } }
  ],
  "output": { "format": "mp4", "resolution": "1920x1080", "preset": "youtube" }
}
```

**Layouts:** `side_by_side` (50/50), `thirds` (33/33/33), `picture_in_picture`, `top_bottom`

**Response:**
```json
{ "job_id": "job_split_xyz", "status": "queued", "estimated_seconds": 60 }
```

---

## 6. Poll Job Status

```http
GET /v1/jobs/{job_id}
```

**In progress:**
```json
{ "job_id": "job_edit_abc001", "status": "processing", "progress": 0.47, "stage": "color_grading" }
```

**Stage values:** `queued` → `assembling` → `color_grading` → `audio_mixing` → `rendering` → `encoding` → `uploading` → `completed` / `failed`

**Completed:**
```json
{
  "job_id": "job_edit_abc001",
  "status": "completed",
  "duration_seconds": 68.5,
  "outputs": {
    "video": "https://cdn.nemovideo.ai/outputs/job_edit_abc001/final.mp4",
    "thumbnail": "https://cdn.nemovideo.ai/outputs/job_edit_abc001/thumb.jpg",
    "preview": "https://cdn.nemovideo.ai/outputs/job_edit_abc001/preview_720p.mp4"
  }
}
```

**Failed:**
```json
{ "job_id": "job_edit_abc001", "status": "failed", "error": "Audio codec incompatible: input contains DTS audio" }
```

**Polling strategy:**
- Short projects (<2 min output): poll every 5s
- Long projects: poll every 15–30s
- Timeout after 30 minutes; surface error to user
- Show `stage` to user during long renders

---

## 7. Download Output

```http
GET <outputs.video>
```

No auth required (pre-signed CDN URLs, valid for **24 hours**).

- `outputs.video` — full-quality final render
- `outputs.preview` — 720p preview for quick review
- `outputs.thumbnail` — JPEG thumbnail

> Always offer the `preview` URL first for large files. Remind user CDN URLs expire in 24h.

---

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 400 | Bad request (invalid timeline) | Check request body; surface specific error |
| 401 | Invalid or missing API key | Prompt user to check `NEMOVIDEO_API_KEY` |
| 413 | File too large | Advise user to compress or split before uploading |
| 422 | Unsupported codec/resolution/parameter | List supported values; suggest re-encoding |
| 429 | Rate limited | Wait 10s; retry with exponential backoff (max 5 retries) |
| 500/503 | Server error | Retry after 30s; surface error if persistent |

For `job.status === "failed"`, always surface the `error` field with a plain explanation and concrete next steps.
