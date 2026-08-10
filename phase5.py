import os                                    # read env vars (my API key)
import json                                  # read config + questions files
import time                                  # for retry pauses
import string                                # gives string.punctuation for cleaning text
import requests                              # send API requests
from dotenv import load_dotenv               # load .env

load_dotenv()

with open("config.json") as f:               # load settings
    config = json.load(f)
with open("questions_open.json") as f:       # load the short-answer questions
    questions = json.load(f)

model = config["models"][0]                  # use the first model in the config
key = os.getenv(model["api_key_env"])        # its API key
url = model["base_url"]                       # its endpoint
headers = {"Authorization": f"Bearer {key}"} # auth header


def call_with_retry(url, headers, payload, max_attempts=4):   # call the API, retry on failure
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            if attempt == max_attempts:
                print(f"    gave up after {attempt} attempts: {error}")
                return None
            time.sleep(2 ** (attempt - 1))


def normalize(text):                         # clean a string down to bare words
    text = text.lower().strip()              # lowercase + trim
    for p in string.punctuation:             # remove every punctuation mark
        text = text.replace(p, "")
    return text.strip()


def fuzzy_match(expected, model_answer):     # DUMB grader: is the expected text inside the answer?
    return normalize(expected) in normalize(model_answer)


def judge_correct(question, expected, model_answer):   # SMART grader: ask a model to judge
    judge_prompt = (                         # give the judge the question, expected, and given answer
        f"Question: {question}\n"
        f"Expected answer: {expected}\n"
        f"Model's answer: {model_answer}\n\n"
        "Is the model's answer correct? Reply with only one word: CORRECT or INCORRECT."
    )
    payload = {"model": model["model_id"], "messages": [{"role": "user", "content": judge_prompt}]}
    data = call_with_retry(url, headers, payload)      # ask the judge model
    if data is None:                         # judge call failed
        return False
    verdict = data["choices"][0]["message"]["content"].strip().upper()  # the judge's reply
    if "INCORRECT" in verdict:               # check the LONGER word first (INCORRECT contains CORRECT)
        return False
    return "CORRECT" in verdict              # otherwise, correct if it said so


fuzzy_score = 0                              # tally for the dumb grader
judge_score = 0                              # tally for the smart grader
for q in questions:                          # loop over each open-ended question
    prompt = q["question"] + "\nAnswer in a few words."   # ask the model to answer briefly
    payload = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}]}

    data = call_with_retry(url, headers, payload)         # get the model's answer
    if data is None:
        print("skipped:", q["question"][:40])
        continue

    model_answer = data["choices"][0]["message"]["content"]           # the free-text answer
    fuzzy = fuzzy_match(q["answer"], model_answer)                     # grade it two ways
    judge = judge_correct(q["question"], q["answer"], model_answer)
    if fuzzy:
        fuzzy_score += 1
    if judge:
        judge_score += 1

    print(f"Q: {q['question'][:45]}")
    print(f"   model: {model_answer.strip()[:55]}")
    print(f"   fuzzy: {'correct' if fuzzy else 'WRONG'}   |   judge: {'correct' if judge else 'WRONG'}\n")

print(f"Fuzzy-match score: {fuzzy_score}/{len(questions)}")     # dumb grader total
print(f"LLM-judge score:   {judge_score}/{len(questions)}")     # smart grader total