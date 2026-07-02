import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("ANTHROPIC_API_KEY")

if key:
    print("Key loaded! Length:", len(key), "characters")
else:
    print("No key found — check your .env file")
