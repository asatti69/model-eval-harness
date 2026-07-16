import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()                          # read my .env file
key = os.getenv("GROQ_API_KEY")        # grab my Groq key

# Load my question set from the file
with open("questions.json") as f:
    questions = json.load(f)

# --- API setup ---
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": f"Bearer {key}"}

correct_count = 0            # tally of how many the model gets right
total = len(questions)       # total number of questions

# Go through every question, numbered starting at 1
for index, q in enumerate(questions, start=1):
    # Build the A/B/C/D option lines
    option_lines = ""
    for letter, text in q["options"].items():
        option_lines += f"{letter}) {text}\n"
    # Assemble the full prompt with a clear instruction
    prompt = f"{q['question']}\n{option_lines}\nAnswer with ONLY the letter (A, B, C, or D)."
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()                       # bad status -> jump to except
        data = response.json()
        model_answer = data["choices"][0]["message"]["content"]
        model_letter = model_answer.strip().upper()[0]    # take the first letter it gave
        is_correct = (model_letter == q["correct"])       # compare to my answer key
        if is_correct:
            correct_count += 1                            # count it if right
        mark = "correct" if is_correct else "WRONG"
        print(f"Q{index}: model said {model_letter}, key says {q['correct']} -> {mark}")
    except requests.exceptions.RequestException as error:
        # one failed call shouldn't stop the whole run
        print(f"Q{index}: API call failed - {error}")

# Final score after the loop finishes
percent = (correct_count / total) * 100
print(f"\nScore: {correct_count}/{total} ({percent:.1f}%)")