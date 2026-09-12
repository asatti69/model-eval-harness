# Model Evaluation Harness

A command-line tool (with a Streamlit dashboard) that runs multiple large language models against a
question set, scores them, tracks token cost, and produces saved, comparable reports — built from
scratch in Python to learn both **how to build an eval** and, more importantly, **why a single
benchmark score usually can't be trusted.**

---

## What it does

- Runs a set of LLMs against a fixed question set and grades their answers
- Works with **multiple providers** through the OpenAI-compatible API standard (provider-agnostic — swap models via config, not code)
- Handles real-world API failures: **retry with exponential backoff**, **concurrency**, graceful error handling
- Tracks **tokens and estimated dollar cost** per model per run
- Grades **multiple-choice** (exact match) *and* **open-ended** answers (fuzzy matching + LLM-as-judge)
- **Saves every run** to a timestamped JSON file so results are reproducible and queryable
- Ships with an interactive **Streamlit dashboard** to explore runs, filter answers, compare runs, and export

## Why benchmark scores can't be trusted (the real lesson)

I proved each of these with evidence from my own runs:

- **Non-determinism** — I ran the identical eval three times and got **85.7%, 85.7%, then 78.6%** with zero changes. Models sample from a probability distribution, so the same question can get a different answer.
- **Small-sample noise** — with only 14 questions, each is worth ~7 points and the margin of error is roughly **±19 points**. A single flipped answer swings the headline number.
- **Comparisons flip** — "which model is better" changed depending on the run; a one-run comparison is close to meaningless.
- **The grader is fallible** — my LLM-as-judge graded a *wrong* answer as **correct 2 out of 5 times** (and was non-deterministic), because a model can't reliably catch a mistake it would make itself.
- **Data contamination** — models may have memorized public test answers during training, so a high score can reflect recall, not reasoning.

**Takeaway:** before believing "Model X scored 92% on benchmark Y," you need the sample size, number of
runs, temperature, whether the benchmark is public (contamination), and how it was graded.

## Tech stack

Python · `requests` · `python-dotenv` · `concurrent.futures` (threads) · `pandas` · **Streamlit** · Git

## How to run

```bash
# 1. Set up
python3 -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Add your API key
echo "GROQ_API_KEY=your_key_here" > .env    # or any OpenAI-compatible provider

# 3. Run an evaluation (saves results to results/)
python phase6.py

# 4. Explore results in the dashboard
streamlit run app.py
```

Models and the question set are configured in `config.json` — adding a model is a config change, no code edits.

## Project structure

- `phase6.py` — the full harness: runs models, scores, retries, concurrency, cost, saves each run
- `app.py` — Streamlit dashboard (comparison table, chart, question explorer, compare runs, export)
- `config.json` — which models to run, their endpoints, and pricing
- `questions.json` / `questions_open.json` — multiple-choice and open-ended question sets
- `results/` — every run saved as a timestamped JSON file
- `NOTES.md` — running log of decisions, bugs, and methodology findings

## What I learned

Real engineering workflow (git, virtual environments, secret management, reproducible dependencies),
API integration and authentication, building for reliability (retries, concurrency, error handling),
data persistence and reporting, building a UI with Streamlit — and, above all, how to **measure model
performance and then distrust that measurement correctly.**

## Possible improvements

- Unify the multiple-choice and open-ended graders into one config-driven harness
- Use a separate, stronger model as the judge instead of self-judging
- Retry only *transient* errors (503/timeout), not permanent ones (404/401)
- Report an average over multiple runs with a confidence interval, not a single score
