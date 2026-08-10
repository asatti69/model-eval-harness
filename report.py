import json
import glob

# Find all saved runs and pick the most recent one
run_files = sorted(glob.glob("results/run_*.json"))   # all run files, oldest -> newest
if not run_files:
    print("No runs found. Run phase6.py first.")
    exit()

latest = run_files[-1]                                 # last in sorted order = newest
print(f"Report for: {latest}\n")

with open(latest) as f:
    run = json.load(f)                                 # reopen the saved run

# Print a comparison table
print(f"{'Model':<14}{'Score':<8}{'Percent':<10}{'Cost':<12}")   # header row
print("-" * 44)
for r in run["results"]:
    percent = (r["correct"] / r["total"]) * 100
    print(f"{r['model']:<14}{r['score']:<8}{percent:<10.1f}${r['cost']:.6f}")