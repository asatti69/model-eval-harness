import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# --- Load settings (config) and data (questions), both from files ---
with open("config.json") as f:
    config = json.load(f)

with open(config["question_file"]) as f:      # NEW: the question file name comes from config
    questions = json.load(f)


# --- NEW: the whole eval, wrapped in a function that takes ONE model + the questions ---
def run_eval(model, questions):
    key = os.getenv(model["api_key_env"])     # NEW: key name comes from config, not hardcoded
    url = model["base_url"]                    # NEW: URL comes from config
    headers = {"Authorization": f"Bearer {key}"}

    correct_count = 0
    total = len(questions)

    for index, q in enumerate(questions, start=1):
        option_lines = ""
        for letter, text in q["options"].items():
            option_lines += f"{letter}) {text}\n"
        prompt = f"{q['question']}\n{option_lines}\nAnswer with ONLY the letter (A, B, C, or D)."
        payload = {
            "model": model["model_id"],        # NEW: model id comes from config
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            model_answer = data["choices"][0]["message"]["content"]
            cleaned = model_answer.strip().upper()
            model_letter = cleaned[0] if cleaned else "?"   # "?" if the model gave nothing
            if model_letter == q["correct"]:
                correct_count += 1
        except requests.exceptions.RequestException as error:
            print(f"  Q{index}: API call failed - {error}")

    return correct_count, total                # NEW: hand the results back to the caller


# --- NEW: run every model listed in the config, one after another ---
for model in config["models"]:
    print(f"\nRunning: {model['name']} ...")
    correct, total = run_eval(model, questions)         # call the function for this model
    percent = (correct / total) * 100
    print(f"{model['name']}: {correct}/{total} ({percent:.1f}%)")