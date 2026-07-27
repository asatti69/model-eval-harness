import os
import time  # NEW (Phase 4): lets me pause between retry attempts
import json
import requests
from dotenv import load_dotenv

load_dotenv()

with open("config.json") as f:
    config = json.load(f)

with open(config["question_file"]) as f:
    questions = json.load(f)


# NEW (Phase 4): makes the API call, retrying with exponential backoff if it fails
def call_with_retry(url, headers, payload, max_attempts=4):
    for attempt in range(1, max_attempts + 1):          # try up to 4 times: 1, 2, 3, 4
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()                       # success -> hand back data, stop retrying
        except requests.exceptions.RequestException as error:
            if attempt == max_attempts:                  # last try also failed -> give up
                print(f"    gave up after {attempt} attempts: {error}")
                return None
            wait = 2 ** (attempt - 1)                    # wait grows: 1s, then 2s, then 4s
            print(f"    attempt {attempt} failed; retrying in {wait}s...")
            time.sleep(wait)                             # pause before the next attempt


def run_eval(model, questions):
    key = os.getenv(model["api_key_env"])
    url = model["base_url"]
    headers = {"Authorization": f"Bearer {key}"}

    correct_count = 0
    total = len(questions)

    for index, q in enumerate(questions, start=1):
        option_lines = ""
        for letter, text in q["options"].items():
            option_lines += f"{letter}) {text}\n"
        prompt = f"{q['question']}\n{option_lines}\nAnswer with ONLY the letter (A, B, C, or D)."
        payload = {
            "model": model["model_id"],
            "messages": [{"role": "user", "content": prompt}],
        }
        data = call_with_retry(url, headers, payload)   # NEW (Phase 4): call now retries internally
        if data is None:                                # NEW (Phase 4): all retries failed for this question
            print(f"  Q{index}: skipped after retries")
            continue                                    # NEW (Phase 4): skip it, keep the run going
        model_answer = data["choices"][0]["message"]["content"]
        cleaned = model_answer.strip().upper()
        model_letter = cleaned[0] if cleaned else "?"
        if model_letter == q["correct"]:
            correct_count += 1

    return correct_count, total


for model in config["models"]:
    print(f"\nRunning: {model['name']} ...")
    correct, total = run_eval(model, questions)
    percent = (correct / total) * 100
    print(f"{model['name']}: {correct}/{total} ({percent:.1f}%)")