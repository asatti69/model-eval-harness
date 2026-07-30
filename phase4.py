import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Load settings and questions
with open("config.json") as f:
    config = json.load(f)

with open(config["question_file"]) as f:
    questions = json.load(f)


# MODULE 1: make the call, retrying with backoff if it fails
def call_with_retry(url, headers, payload, max_attempts=4):
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            if attempt == max_attempts:
                print(f"    gave up after {attempt} attempts: {error}")
                return None
            wait = 2 ** (attempt - 1)
            print(f"    attempt {attempt} failed; retrying in {wait}s...")
            time.sleep(wait)


def run_eval(model, questions):
    key = os.getenv(model["api_key_env"])
    url = model["base_url"]
    headers = {"Authorization": f"Bearer {key}"}

    correct_count = 0
    total = len(questions)
    prompt_tokens_total = 0           # MODULE 2: accumulator for input tokens
    completion_tokens_total = 0       # MODULE 2: accumulator for output tokens

    for index, q in enumerate(questions, start=1):
        option_lines = ""
        for letter, text in q["options"].items():
            option_lines += f"{letter}) {text}\n"
        prompt = f"{q['question']}\n{option_lines}\nAnswer with ONLY the letter (A, B, C, or D)."
        payload = {
            "model": model["model_id"],
            "messages": [{"role": "user", "content": prompt}],
        }

        data = call_with_retry(url, headers, payload)
        if data is None:
            print(f"  Q{index}: skipped after retries")
            continue

        usage = data["usage"]                                   # MODULE 2: read this call's tokens
        prompt_tokens_total += usage["prompt_tokens"]
        completion_tokens_total += usage["completion_tokens"]

        model_answer = data["choices"][0]["message"]["content"]
        cleaned = model_answer.strip().upper()
        model_letter = cleaned[0] if cleaned else "?"
        if model_letter == q["correct"]:
            correct_count += 1

    # MODULE 2: tokens -> dollars, then return a labelled dictionary
    input_cost = (prompt_tokens_total / 1_000_000) * model["price_in_per_1m"]
    output_cost = (completion_tokens_total / 1_000_000) * model["price_out_per_1m"]
    cost = input_cost + output_cost

    return {
        "correct": correct_count,
        "total": total,
        "prompt_tokens": prompt_tokens_total,
        "completion_tokens": completion_tokens_total,
        "cost": cost,
    }


for model in config["models"]:
    print(f"\nRunning: {model['name']} ...")
    result = run_eval(model, questions)
    percent = (result["correct"] / result["total"]) * 100
    tokens = result["prompt_tokens"] + result["completion_tokens"]
    print(f"{model['name']}: {result['correct']}/{result['total']} ({percent:.1f}%)")
    print(f"    tokens used: {tokens}  |  estimated cost: ${result['cost']:.6f}")