import os                                                    # read environment variables (my API key)
import time                                                  # pause the program (for retry waits)
import json                                                  # read/parse the JSON config + questions files
import requests                                              # send HTTP requests to the model's API
from concurrent.futures import ThreadPoolExecutor            # run several questions at once (concurrency)
from dotenv import load_dotenv                               # load my .env so my key is available

load_dotenv()                                                # actually read .env into the environment

with open("config.json") as f:                               # open the settings file
    config = json.load(f)                                    # turn its JSON into a Python dictionary

with open(config["question_file"]) as f:                     # open the questions file named in config
    questions = json.load(f)                                 # turn its JSON into a Python list


def call_with_retry(url, headers, payload, max_attempts=4):  # make one API call, retrying if it fails
    for attempt in range(1, max_attempts + 1):               # try up to 4 times: 1, 2, 3, 4
        try:                                                 # attempt the risky network call
            response = requests.post(url, headers=headers, json=payload, timeout=30)  # send it, max 30s wait
            response.raise_for_status()                      # if status is an error, raise it -> except
            return response.json()                           # success: hand back data and STOP retrying
        except requests.exceptions.RequestException as error:  # runs only if the call failed
            if attempt == max_attempts:                      # was that the last allowed try?
                print(f"    gave up after {attempt} attempts: {error}")  # report giving up
                return None                                  # signal failure to the caller
            wait = 2 ** (attempt - 1)                        # growing wait: 1, then 2, then 4 seconds
            print(f"    attempt {attempt} failed; retrying in {wait}s...")  # tell me it's retrying
            time.sleep(wait)                                 # pause, then the loop tries again


def run_eval(model, questions):                              # run the whole eval for ONE model
    key = os.getenv(model["api_key_env"])                    # this model's key, by the name in config
    url = model["base_url"]                                  # this model's endpoint URL, from config
    headers = {"Authorization": f"Bearer {key}"}             # header that proves I'm allowed to call

    def grade_question(q):                                   # helper: handle ONE question, return its result
        option_lines = ""                                    # empty string to build the A/B/C/D lines
        for letter, text in q["options"].items():            # loop over each option (letter + its text)
            option_lines += f"{letter}) {text}\n"            # add "A) Modified\n" etc. to the string
        prompt = f"{q['question']}\n{option_lines}\nAnswer with ONLY the letter (A, B, C, or D)."  # full prompt
        payload = {                                          # the OpenAI-standard request body
            "model": model["model_id"],                      # which model to ask
            "messages": [{"role": "user", "content": prompt}],  # my question as a user message
        }
        data = call_with_retry(url, headers, payload)        # make the call (retries built in)
        if data is None:                                     # failed even after retries
            return {"correct": False, "prompt_tokens": 0, "completion_tokens": 0}  # count wrong, no tokens
        usage = data["usage"]                                # the token counts for this call
        model_answer = data["choices"][0]["message"]["content"]  # dig out the model's answer text
        cleaned = model_answer.strip().upper()               # trim spaces, make uppercase
        model_letter = cleaned[0] if cleaned else "?"        # first letter, or "?" if answer was empty
        return {                                             # hand back this question's result
            "correct": model_letter == q["correct"],         # True if it matches my answer key
            "prompt_tokens": usage["prompt_tokens"],         # input tokens used
            "completion_tokens": usage["completion_tokens"], # output tokens used
        }

    with ThreadPoolExecutor(max_workers=5) as pool:          # a pool of 5 workers running in parallel
        results = list(pool.map(grade_question, questions))  # grade all questions concurrently, keep order

    correct_count = 0                                        # accumulator: number correct
    prompt_tokens_total = 0                                  # accumulator: total input tokens
    completion_tokens_total = 0                              # accumulator: total output tokens
    for r in results:                                        # go through each question's result
        if r["correct"]:                                     # if this question was right
            correct_count += 1                               # add one to the correct tally
        prompt_tokens_total += r["prompt_tokens"]            # add its input tokens
        completion_tokens_total += r["completion_tokens"]    # add its output tokens

    total = len(questions)                                   # how many questions in total
    input_cost = (prompt_tokens_total / 1_000_000) * model["price_in_per_1m"]      # $ for input tokens
    output_cost = (completion_tokens_total / 1_000_000) * model["price_out_per_1m"]  # $ for output tokens
    cost = input_cost + output_cost                          # total estimated cost

    return {                                                 # return everything as a labelled dictionary
        "correct": correct_count,                            # number correct
        "total": total,                                      # number of questions
        "prompt_tokens": prompt_tokens_total,                # total input tokens
        "completion_tokens": completion_tokens_total,        # total output tokens
        "cost": cost,                                        # estimated dollar cost
    }


for model in config["models"]:                              # loop over every model in the config
    print(f"\nRunning: {model['name']} ...")                 # announce which model is running
    result = run_eval(model, questions)                      # run the eval, get back the results dict
    percent = (result["correct"] / result["total"]) * 100    # turn the score into a percentage
    tokens = result["prompt_tokens"] + result["completion_tokens"]  # total tokens used
    print(f"{model['name']}: {result['correct']}/{result['total']} ({percent:.1f}%)")  # print the score
    print(f"    tokens used: {tokens}  |  estimated cost: ${result['cost']:.6f}")  # print tokens + cost