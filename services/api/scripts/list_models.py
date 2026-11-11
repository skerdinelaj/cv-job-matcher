"""List the Gemini models my API key can use right now.

Google renames and retires models often, so we never guess a model name:
we run this script, pick one chat model and one embedding model,
and put them in .env (GEMINI_CHAT_MODEL / GEMINI_EMBED_MODEL).

Run from services/api:  python scripts/list_models.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# .env lives in the repo root: services/api/scripts/list_models.py -> up 3 folders
ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")


def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("GEMINI_API_KEY is missing. Copy .env.example to .env and add your key.")

    client = genai.Client(api_key=api_key)

    chat_models: list[str] = []
    embed_models: list[str] = []

    # Each model says which actions it supports, e.g. "generateContent" or "embedContent"
    for model in client.models.list():
        actions: list[str] = model.supported_actions or []
        name = model.name or "?"
        if "generateContent" in actions:
            chat_models.append(name)
        if "embedContent" in actions:
            embed_models.append(name)

    print("Chat models (generateContent):")
    for name in sorted(chat_models):
        print(f"  {name}")

    print("\nEmbedding models (embedContent):")
    for name in sorted(embed_models):
        print(f"  {name}")


if __name__ == "__main__":
    main()
