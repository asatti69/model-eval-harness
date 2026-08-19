import json                                    # read the saved run files (JSON)
import glob                                    # find files by pattern (all run files)


# =========================================================================
# pick_run: show every saved run and let the user choose which one to open
# =========================================================================
def pick_run():
    run_files = sorted(glob.glob("results/run_*.json"))   # find all run files, oldest -> newest
    if not run_files:                                     # if the list is empty (no runs saved yet)
        print("No runs found. Run phase6.py first.")
        return None                                       # hand back nothing
    print("\nSaved runs:")
    for i, f in enumerate(run_files, start=1):            # number each file 1, 2, 3...
        print(f"  {i}. {f}")                              # show "1. results/run_..."
    choice = int(input("Pick a run number: "))            # ask which; int() turns the text into a number
    with open(run_files[choice - 1]) as f:                # open that file (choice-1: lists start at 0)
        return json.load(f)                               # read it into a Python dict and return it


# =========================================================================
# pick_model: show the models in a run and let the user choose one
# =========================================================================
def pick_model(run):
    models = run["results"]                               # the list of model results in this run
    print("\nModels in this run:")
    for i, m in enumerate(models, start=1):               # number each model
        print(f"  {i}. {m['model']}  ({m['score']})")     # show "1. grok baby  (12/14)"
    choice = int(input("Pick a model number: "))          # ask which model
    return models[choice - 1]                             # return the chosen model (0-based index)


# =========================================================================
# show_questions: list the questions; optionally only correct or only wrong
# =========================================================================
def show_questions(model, only=None):
    for i, a in enumerate(model["answers"], start=1):     # go through each question's result, numbered
        if only == "correct" and not a["is_correct"]:     # filtering to correct? skip the wrong ones
            continue                                      # jump straight to the next question
        if only == "incorrect" and a["is_correct"]:       # filtering to wrong? skip the correct ones
            continue
        mark = "correct" if a["is_correct"] else "WRONG"  # label for this question
        print(f"  {i}. [{mark}] {a['question'][:60]}")    # show "3. [WRONG] question text..."


# =========================================================================
# show_one: show full detail for a single chosen question
# =========================================================================
def show_one(model):
    show_questions(model)                                 # first list all questions so the user can pick
    n = int(input("Pick a question number: "))            # ask which one
    a = model["answers"][n - 1]                           # grab that question's record (n-1 = 0-based)
    print(f"\nQuestion {n}: {a['question']}")             # the full question text
    print(f"  Model answered: {a['model_answer']}")       # what the model picked
    print(f"  Correct answer: {a['correct']}")            # the right answer
    print("  Result:", "correct" if a["is_correct"] else "WRONG")  # right or wrong


# =========================================================================
# main program: pick a run, pick a model, then loop the menu until quit
# =========================================================================
run = pick_run()                                          # choose a run to inspect
if run:                                                   # only continue if a run was loaded
    model = pick_model(run)                               # choose a model within that run
    while True:                                           # repeat the menu forever, until we 'break'
        print("\n--- MENU ---")
        print("1. List all questions")
        print("2. Show only CORRECT")
        print("3. Show only INCORRECT")
        print("4. Pick a question for full detail")
        print("5. Switch model")
        print("6. Switch run")
        print("7. Quit")
        choice = input("Choose an option: ").strip()      # read the menu choice (as text)

        if choice == "1":                                 # option 1: list everything
            show_questions(model)
        elif choice == "2":                               # option 2: only correct
            show_questions(model, only="correct")
        elif choice == "3":                               # option 3: only incorrect
            show_questions(model, only="incorrect")
        elif choice == "4":                               # option 4: full detail for one question
            show_one(model)
        elif choice == "5":                               # option 5: pick a different model
            model = pick_model(run)
        elif choice == "6":                               # option 6: pick a different run
            run = pick_run()
            model = pick_model(run)
        elif choice == "7":                               # option 7: leave the program
            print("Bye!")
            break                                         # exit the while loop -> program ends
        else:                                             # anything else: not a valid choice
            print("Not a valid option.")