"""
Vocalizer API — Interactive Test Client

Run this script to test all API endpoints from the command line.
Requires: pip install httpx

Usage:
    python test_client.py

Make sure the server is running (python main.py) before running this.
"""

import asyncio
import os
import sys
import struct
import math
import httpx

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "change-me")

HEADERS = {"X-API-Key": API_KEY}


def generate_test_wav(duration_s: float = 2.0, freq: float = 440.0, sample_rate: int = 16000) -> bytes:
    """Generate a simple WAV file with a sine wave tone for testing."""
    num_samples = int(sample_rate * duration_s)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        value = int(32767 * 0.5 * math.sin(2 * math.pi * freq * t))
        samples.append(struct.pack("<h", value))

    audio_data = b"".join(samples)
    data_size = len(audio_data)
    file_size = 36 + data_size

    wav = b"RIFF"
    wav += struct.pack("<I", file_size)
    wav += b"WAVE"
    wav += b"fmt "
    wav += struct.pack("<I", 16)          # chunk size
    wav += struct.pack("<H", 1)           # PCM
    wav += struct.pack("<H", 1)           # mono
    wav += struct.pack("<I", sample_rate)  # sample rate
    wav += struct.pack("<I", sample_rate * 2)  # byte rate
    wav += struct.pack("<H", 2)           # block align
    wav += struct.pack("<H", 16)          # bits per sample
    wav += b"data"
    wav += struct.pack("<I", data_size)
    wav += audio_data

    return wav


async def test_health(client: httpx.AsyncClient):
    print("\n=== Health Check ===")
    r = await client.get(f"{BASE_URL}/health")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")


async def test_stt(client: httpx.AsyncClient):
    print("\n=== Speech-to-Text ===")
    print("(Sending a test tone — Whisper will likely return empty or noise)")

    wav_data = generate_test_wav()
    r = await client.post(
        f"{BASE_URL}/stt/",
        headers=HEADERS,
        files={"audio": ("test.wav", wav_data, "audio/wav")},
        timeout=30,
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print(f"Transcript: {r.json()}")
    else:
        print(f"Error: {r.text}")


async def test_llm(client: httpx.AsyncClient):
    print("\n=== LLM Chat ===")

    messages = [
        "Hey! What's up?",
        "Remember that my favorite color is blue.",
        "What's my favorite color?",
    ]

    for msg in messages:
        print(f"\nUser: {msg}")
        r = await client.post(
            f"{BASE_URL}/llm/",
            headers=HEADERS,
            json={"message": msg, "user_id": "test-user"},
            timeout=30,
        )
        if r.status_code == 200:
            print(f"Assistant: {r.json()['response']}")
        else:
            print(f"Error ({r.status_code}): {r.text}")


async def test_tts(client: httpx.AsyncClient):
    print("\n=== Text-to-Speech ===")

    r = await client.post(
        f"{BASE_URL}/tts/",
        headers=HEADERS,
        json={"text": "Hello! I'm the vocalizer assistant. Pretty cool, right?"},
        timeout=30,
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        out_path = "test_output.mp3"
        with open(out_path, "wb") as f:
            f.write(r.content)
        size_kb = len(r.content) / 1024
        print(f"Audio saved to {out_path} ({size_kb:.1f} KB)")
    else:
        print(f"Error: {r.text}")


async def test_conversation(client: httpx.AsyncClient):
    print("\n=== Full Conversation Pipeline ===")
    print("(Sending test tone — result depends on Whisper transcription)")

    wav_data = generate_test_wav()
    r = await client.post(
        f"{BASE_URL}/conversation/",
        headers=HEADERS,
        files={"audio": ("test.wav", wav_data, "audio/wav")},
        data={"user_id": "test-user"},
        timeout=60,
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        transcript = r.headers.get("X-Transcript", "(none)")
        response = r.headers.get("X-Response", "(none)")
        print(f"Transcript: {transcript}")
        print(f"LLM Response: {response}")
        out_path = "test_conversation.mp3"
        with open(out_path, "wb") as f:
            f.write(r.content)
        size_kb = len(r.content) / 1024
        print(f"Audio saved to {out_path} ({size_kb:.1f} KB)")
    else:
        print(f"Error: {r.text}")


async def test_clear_memories(client: httpx.AsyncClient):
    print("\n=== Clear Memories ===")
    r = await client.delete(
        f"{BASE_URL}/llm/memories",
        headers=HEADERS,
        params={"user_id": "test-user"},
        timeout=10,
    )
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")


async def main():
    print("=" * 50)
    print("  Vocalizer API — Test Client")
    print(f"  Server: {BASE_URL}")
    print("=" * 50)

    async with httpx.AsyncClient() as client:
        await test_health(client)

        # Test auth rejection
        print("\n=== Auth Rejection Test ===")
        r = await client.post(
            f"{BASE_URL}/llm/",
            headers={"X-API-Key": "wrong-key"},
            json={"message": "test"},
        )
        print(f"Bad key → Status: {r.status_code} (expected 401)")

        await test_stt(client)
        await test_llm(client)
        await test_tts(client)
        await test_conversation(client)
        await test_clear_memories(client)

    print("\n" + "=" * 50)
    print("  All tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
