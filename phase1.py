import os                              # lets me read environment variables (like my API key)
import requests                        # lets me send HTTP requests over the internet
from dotenv import load_dotenv         # loads my .env file so my code can read my secret key

load_dotenv()                          # read the .env file into memory
key = os.getenv("GROQ_API_KEY")        # grab my Groq key by its name in .env

# The address of Groq's OpenAI-compatible endpoint — the "window" I send my question to
url = "https://api.groq.com/openai/v1/chat/completions"

# Headers carry my key so the server knows I'm allowed. "Bearer <key>" is the standard format.
headers = {"Authorization": f"Bearer {key}"}

# The payload is my "order form" in OpenAI-standard shape
payload = {
    "model": "openai/gpt-oss-20b",     # which model on Groq I want to answer
    "messages": [                      # the conversation, as a list of messages
        {"role": "user", "content": "what is the capital of France"}  # my question
    ],
}

try:
    # Send the request to Groq; give up after 30 seconds so it can't hang forever
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    # If the server returned an error status (404, 429, 503...), jump down to except
    response.raise_for_status()
    # Turn the raw reply text into Python data (a dictionary) I can dig through
    data = response.json()
    # Slice into the JSON to grab just the answer:
    # "choices" is a list -> take the first item [0] -> its "message" -> its "content"
    answer = data["choices"][0]["message"]["content"]
    # Print only the clean answer, no JSON clutter
    print("Answer:", answer)
except requests.exceptions.RequestException as error:
    # If anything failed (network, timeout, bad status), show a friendly message instead of crashing
    print("Something went wrong with the API call:", error)