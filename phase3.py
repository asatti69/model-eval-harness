import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

#  Load settings (config) and data (questions), both from files 
with open("config.json") as f:
    config = json.load(f)

with open(config["question_file"]) as f:      # the question file name comes from config
    questions = json.load(f)


#  the whole eval, wrapped in a function that takes ONE model + the questions
def run_eval(model, questions):
    key = os.getenv(model["api_key_env"])     #  key name comes from config, not hardcoded
    url = model["base_url"]                    # URL comes from config
    headers = {"Authorization": f"Bearer {key}"}

    correct_count = 0
    total = len(questions)

    for index, q in enumerate(questions, start=1):
        option_lines = ""
        for letter, text in q["options"].items():
            option_lines += f"{letter}) {text}\n".  # used an Fstring storing each option letter and the answer choice after each new line starts
        prompt = f"{q['question']}\n{option_lines}\nAnswer with ONLY the letter (A, B, C, or D)." # another fstring in which it glues the whole prompt, Q , options , and command
        payload = {
            "model": model["model_id"],        # wraps the whole question in an Openai order
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status(). #error check for the network status
            data = response.json()
            model_answer = data["choices"][0]["message"]["content"]  
            cleaned = model_answer.strip().upper()
            model_letter = cleaned[0] if cleaned else "?"   # "?" if the model gave nothing, also to clean the index error crash as a empty response could be a valid response but it doesnt mean it should fail the code 
            if model_letter == q["correct"]:
                correct_count += 1
        except requests.exceptions.RequestException as error:
            print(f"  Q{index}: API call failed - {error}")

    return correct_count, total                # NEW: hand the results back to the caller


#  run every model listed in the config, one after another 
for model in config["models"]:
    print(f"\nRunning: {model['name']} ...")
    correct, total = run_eval(model, questions)         # call the function for this model
    percent = (correct / total) * 100
    print(f"{model['name']}: {correct}/{total} ({percent:.1f}%)")