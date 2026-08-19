import json                                    # read saved run files (JSON)
import glob                                    # find all run files by pattern


# =========================================================================
# list_run_files: return every saved run file, sorted oldest -> newest
# =========================================================================
def list_run_files():
    return sorted(glob.glob("results/run_*.json"))       # wildcard match, sorted by name (= by time)


# =========================================================================
# pick_run_file: show all runs, let the user choose one, return its name + data
# =========================================================================
def pick_run_file():
    files = list_run_files()                             # get the list of run files
    if not files:                                        # none saved yet
        print("No runs found. Run phase6.py first.")
        return None, None                                # return two "nothings"
    print("\nSaved runs:")
    for i, f in enumerate(files, start=1):               # number each file
        print(f"  {i}. {f}")
    choice = int(input("Pick a run number: "))           # ask which one
    filename = files[choice - 1]                         # choice-1 because lists start at 0
    with open(filename) as f:
        return filename, json.load(f)                    # hand back BOTH the name and the loaded data


# =========================================================================
# build_table: turn one run into a list of text lines (reused for print AND export)
# =========================================================================
def build_table(run):
    lines = []                                           # start with an empty list of lines
    lines.append(f"{'Model':<14}{'Score':<8}{'Percent':<10}{'Cost':<12}")   # header row
    lines.append("-" * 44)                               # a divider line of 44 dashes
    for r in run["results"]:                             # one line per model
        percent = (r["correct"] / r["total"]) * 100      # score as a percentage
        lines.append(f"{r['model']:<14}{r['score']:<8}{percent:<10.1f}${r['cost']:.6f}")
    return lines                                         # hand back all the lines


# =========================================================================
# show_table: print a run's table to the screen
# =========================================================================
def show_table(run):
    for line in build_table(run):                        # get the lines and print each one
        print(line)


# =========================================================================
# compare_two: pick two runs and show their tables so you can compare
# =========================================================================
def compare_two():
    print("\n--- FIRST run ---")
    name1, run1 = pick_run_file()                        # choose run A
    print("\n--- SECOND run ---")
    name2, run2 = pick_run_file()                        # choose run B
    if run1 is None or run2 is None:                     # user had no runs to pick
        return
    print(f"\nRun A: {name1}")                           # show run A's table
    show_table(run1)
    print(f"\nRun B: {name2}")                           # show run B's table
    show_table(run2)


# =========================================================================
# breakdown: show which questions each model got right/wrong in a run
# =========================================================================
def breakdown():
    name, run = pick_run_file()                          # choose a run
    if run is None:
        return
    for r in run["results"]:                             # for each model
        print(f"\n{r['model']} ({r['score']}):")
        for i, a in enumerate(r["answers"], start=1):    # for each question
            mark = "correct" if a["is_correct"] else "WRONG"
            print(f"  Q{i}: [{mark}] {a['question'][:50]}")


# =========================================================================
# export: save a run's table to a text file
# =========================================================================
def export():
    name, run = pick_run_file()                          # choose a run
    if run is None:
        return
    out_name = name.replace("results/", "report_").replace(".json", ".txt")  # build an output filename
    with open(out_name, "w") as f:                       # 'w' = write mode (creates the file)
        f.write(f"Report for {name}\n\n")                # write a title line
        for line in build_table(run):                    # write each table line
            f.write(line + "\n")                         # add a newline after each
    print(f"Saved report to {out_name}")


# =========================================================================
# main menu: loop until the user quits
# =========================================================================
while True:                                              # keep showing the menu
    print("\n=== REPORT MENU ===")
    print("1. Report on a run")
    print("2. Compare two runs")
    print("3. Per-question breakdown")
    print("4. Export a run's report to a file")
    print("5. Quit")
    choice = input("Choose an option: ").strip()         # read the choice

    if choice == "1":                                    # option 1: table for one chosen run
        name, run = pick_run_file()
        if run:
            print(f"\nReport for {name}\n")
            show_table(run)
    elif choice == "2":                                  # option 2: compare two runs
        compare_two()
    elif choice == "3":                                  # option 3: per-question breakdown
        breakdown()
    elif choice == "4":                                  # option 4: export to a file
        export()
    elif choice == "5":                                  # option 5: quit
        print("Bye!")
        break
    else:                                                # anything else
        print("Not a valid option.")