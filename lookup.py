import json
import glob

# Load the most recent run
run_files = sorted(glob.glob("results/run_*.json"))
if not run_files:
    print("No runs found.")
    exit()
with open(run_files[-1]) as f:
    run = json.load(f)

print(f"Looking up run: {run_files[-1]}")
print("Models in this run:", ", ".join(r["model"] for r in run["results"]))

# Ask what to look up
wanted_model = input("Which model? ").strip()
q_number = int(input("Which question number? "))

# Find that model, then that question
found = False
for r in run["results"]:
    if r["model"] == wanted_model:
        found = True
        answer = r["answers"][q_number - 1]          # question 7 = list index 6
        print(f"\nQuestion {q_number}: {answer['question']}")
        print(f"  Model answered: {answer['model_answer']}")
        print(f"  Correct answer: {answer['correct']}")
        print("  Result:", "correct" if answer["is_correct"] else "WRONG")
        break

if not found:
    print("That model isn't in this run.")