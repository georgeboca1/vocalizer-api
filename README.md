# Vocalizer API

High-performance voice conversation API designed for ESP32. Converts speech to text, processes it through an LLM, and returns spoken audio — all optimized for low-bandwidth, memory-constrained devices.

## Architecture

```
ESP32 (mic) ──audio──► /conversation ──► STT (Groq Whisper)
                                          │
                                          ▼
ESP32 (speaker) ◄──mp3── TTS (Edge TTS) ◄── LLM (Groq Llama 3.3 70B)
```

**One request, one response.** The `/conversation` endpoint handles the full pipeline to minimize ESP32 round-trips.

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Server | Python + FastAPI | Async, fast, minimal overhead |
| STT | Groq Whisper Large v3 | Fastest cloud Whisper inference |
| LLM | Groq Llama 3.3 70B | Fastest LLM inference, free tier |
| TTS | Microsoft Edge TTS | Free, fast, natural voices |
| Memory | SQLite (async) | Lightweight persistence |
| Auth | API Key (X-API-Key header) | Simple, secure enough for device auth |

## Setup

### 1. Prerequisites
- Python 3.11+
- A free [Groq API key](https://console.groq.com)

### 2. Install

```bash
# Clone / navigate to the project
cd vocalizer-api

# Create virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure

```bash
# Copy the example env file
copy .env.example .env    # Windows
# cp .env.example .env    # Linux/Mac

# Edit .env and set your keys:
# - GROQ_API_KEY: your Groq API key
# - API_KEY: a secret key for ESP32 authentication (generate something random)
```

### 4. Run

```bash
python main.py
```

Server starts at `http://localhost:8080`. API docs available at `http://localhost:8080/docs`.

### 5. Expose via Cloudflare Tunnel

```bash
cloudflared tunnel --url http://localhost:8080
```

## API Endpoints

All endpoints (except `/health`) require the `X-API-Key` header.

### `GET /health`
Health check. No auth required.

### `POST /stt/`
**Speech-to-Text.** Upload audio, get text back.

```bash
curl -X POST http://localhost:8000/stt/ \
  -H "X-API-Key: your-key" \
  -F "audio=@recording.wav"
```

Response: `{"text": "hello how are you"}`

### `POST /llm/`
**LLM Chat.** Send text, get a response. Supports memory.

```bash
curl -X POST http://localhost:8000/llm/ \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"message": "Remember my name is Alex", "user_id": "esp32-1"}'
```

Response: `{"response": "Got it, Alex! I'll remember that."}`

### `POST /tts/`
**Text-to-Speech.** Send text, get MP3 audio back.

```bash
curl -X POST http://localhost:8000/tts/ \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world!"}' \
  --output speech.mp3
```

### `POST /conversation/`
**Full pipeline (recommended for ESP32).** Audio in → text → LLM → audio out.

```bash
curl -X POST http://localhost:8000/conversation/ \
  -H "X-API-Key: your-key" \
  -F "audio=@recording.wav" \
  -F "user_id=esp32-1" \
  --output response.mp3
```

Response headers include `X-Transcript` (what was heard) and `X-Response` (what the LLM said).

### `DELETE /llm/memories?user_id=esp32-1`
Clear stored memories for a user.

## Testing

```bash
# Make sure the server is running first
python main.py

# In another terminal
python test_client.py
```

The test client will:
1. Check server health
2. Verify auth rejection with a bad key
3. Test STT with a generated tone
4. Test LLM chat with memory (stores and recalls info)
5. Test TTS (saves MP3 to `test_output.mp3`)
6. Test full conversation pipeline
7. Clean up test memories

## ESP32 Integration Notes

- **Audio format**: Send WAV (16-bit PCM, mono, 16kHz) for best STT results
- **Response format**: MP3 audio — use an MP3 decoder library on ESP32 (e.g., libhelix-mp3)
- **Single endpoint**: Use `/conversation/` to minimize network round-trips
- **Auth**: Store the API key in ESP32 flash, send as `X-API-Key` header
- **Memory**: Use a consistent `user_id` per device to maintain conversation memory

## Configuration

All configuration is via environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | (required) | Your Groq API key |
| `API_KEY` | `change-me` | Secret key for ESP32 auth |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |
| `TTS_VOICE` | `en-US-GuyNeural` | Edge TTS voice |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Groq LLM model |
| `STT_MODEL` | `whisper-large-v3` | Groq STT model |
| `AUDIO_BITRATE` | `32k` | MP3 bitrate for TTS output |
