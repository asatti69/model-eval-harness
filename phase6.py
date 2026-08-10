import os
import time
import json
import requests
from datetime import datetime                          #  for timestamps
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

with open("config.json") as f:
    config = json.load(f)

with open(config["question_file"]) as f:
    questions = json.load(f)


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

    def grade_question(q):
        option_lines = ""
        for letter, text in q["options"].items():
            option_lines += f"{letter}) {text}\n"
        prompt = f"{q['question']}\n{option_lines}\nAnswer with ONLY the letter (A, B, C, or D)."
        payload = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}]}
        data = call_with_retry(url, headers, payload)
        if data is None:
            return {"question": q["question"], "model_answer": "?", "correct": q["correct"],
                    "is_correct": False, "prompt_tokens": 0, "completion_tokens": 0}
        usage = data["usage"]
        model_answer = data["choices"][0]["message"]["content"]
        cleaned = model_answer.strip().upper()
        model_letter = cleaned[0] if cleaned else "?"
        return {
            "question": q["question"],                        # the question text
            "model_answer": model_letter,                     #  what the model picked
            "correct": q["correct"],                          # right answer
            "is_correct": model_letter == q["correct"],       # right or wrong (True/False)
            "prompt_tokens": usage["prompt_tokens"],
            "completion_tokens": usage["completion_tokens"],
        }

    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(grade_question, questions))

    correct_count = 0
    prompt_tokens_total = 0
    completion_tokens_total = 0
    for r in results:
        if r["is_correct"]:                                   #  use the True/False field
            correct_count += 1
        prompt_tokens_total += r["prompt_tokens"]
        completion_tokens_total += r["completion_tokens"]

    total = len(questions)
    input_cost = (prompt_tokens_total / 1_000_000) * model["price_in_per_1m"]
    output_cost = (completion_tokens_total / 1_000_000) * model["price_out_per_1m"]
    cost = input_cost + output_cost

    return {
        "model": model["name"],                              #  which model
        "score": f"{correct_count}/{total}",                 #  readable score
        "correct": correct_count,
        "total": total,
        "prompt_tokens": prompt_tokens_total,
        "completion_tokens": completion_tokens_total,
        "cost": cost,
        "answers": results,                                  # every question's detail
    }


all_results = []                                             # collect each model's result
for model in config["models"]:
    print(f"\nRunning: {model['name']} ...")
    result = run_eval(model, questions)
    all_results.append(result)                               # keep it the same
    percent = (result["correct"] / result["total"]) * 100
    tokens = result["prompt_tokens"] + result["completion_tokens"]
    print(f"{model['name']}: {result['correct']}/{result['total']} ({percent:.1f}%)")
    print(f"    tokens used: {tokens}  |  estimated cost: ${result['cost']:.6f}")

# build the run record and save it to a timestamped file
run_record = {
    "timestamp": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
    "question_file": config["question_file"],
    "results": all_results,
}
os.makedirs("results", exist_ok=True)                        # create results/ folder if missing
filename = f"results/run_{run_record['timestamp']}.json"
with open(filename, "w") as f:
    json.dump(run_record, f, indent=2)                       # write the whole run as JSON
print(f"\nSaved run to {filename}")