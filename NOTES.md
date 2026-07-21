# NOTES.md — decisions, things that broke, questions

> Running log for check-ins with Nick. Not a how-to (that's `Project-Cheatsheet.md`) — this is
> *why I made choices*, *what broke*, and *what I still need to ask*.

## Decisions (and why)

- **Dropped Anthropic, went to a free provider.** Per Nick's direction: build on the **OpenAI standard
  chat endpoint**, stay **provider-agnostic**, and don't eval Anthropic (already benchmarked). Also a
  lesson — Claude leaned toward Anthropic because it's made by Anthropic (bias to distrust).
- **First provider = Google Gemini**, now **switching to Groq** because Gemini's free tier kept failing.
- **`.env` variable named `GEMINI_API_KEY`.** The name is mine to choose; naming by provider scales when
  I add more providers later.
- **Using the `requests` library (not an official SDK).** I want to see the raw HTTP mechanics (headers,
  JSON body, status codes) — matches the spec and Nick. Can revisit later.
- **Pin exact model names** (e.g. `gemini-3.1-flash-lite`), not "latest" aliases, so eval runs are
  reproducible and I always know which model produced a score.

## Things that broke (and what I learned)

- **Mismatched quotes** in a command → terminal showed `dquote>`. Fix: Ctrl+C, redo with matching quotes.
- **`cat.env` → command not found.** Needed a space: `cat .env` (command and filename are separate words).
- **nano kept closing before saving** → `.env` ended up empty. Switched to `echo '...' > .env`, which
  writes and saves in one step.
- **`404` NOT_FOUND** — `gemini-2.5-flash` got deprecated. Lesson: model names retire fast; verify against
  the provider's live models page and pin a current one.
- **`503` UNAVAILABLE** — Gemini free tier "high demand" on every Flash variant. It's a *transient* error;
  Phase 4 (retry with backoff) is built to auto-handle exactly this. Decided to switch to Groq for reliability.

## Open questions for Nick

- OK to use **Groq** as my primary model given Gemini's free tier was too flaky?
- Which free providers do you want in my **comparison set** (Groq + Cerebras? + Gemini when it's up)?
- Confirm **`requests` vs official SDK** — I'm using `requests` on purpose to learn the mechanics.
- Any **spending or rate-limit constraints** I should design around?

## Deviations from the spec's tech defaults (spec said to record these)

- **Model provider:** Gemini/Groq instead of Anthropic — per Nick's redirection.
- **Talking to models via OpenAI-compatible endpoints** across providers (keeps the harness provider-agnostic).

## Phase 3 — config-driven + first model comparison

- ✅ Split engine / data / settings: `config.json` lists the question file and the models; `phase3.py`
  reads it and loops. Wrapped the eval in a **function** `run_eval(model, questions)`.
- ✅ Adding a 2nd model (`gpt-oss-120b`) was a **config-only** change — zero code edits. Requirement met.

**Bug I hit + lesson:** `IndexError: string index out of range` — the model sometimes returns an EMPTY
answer, and `[0]` on an empty string crashes. Worse, my `try/except` only caught `RequestException`
(network errors), so this *parsing* error slipped past and killed the whole run. **Lesson: error
handling only covers the failures you anticipate.** Fixed with `cleaned[0] if cleaned else "?"`.

**Comparison experiment (gpt-oss-20b vs gpt-oss-120b), 3 runs:**
- Run 1: 85.7% vs 85.7% (tie) | Run 2: 78.6% vs 92.9% (+14) | Run 3: 78.6% vs 85.7% (+7)
- Averages: ~81% vs ~88%. **Which is "better" depends on which single run you look at** — run 1 says
  tie, run 2 says a blowout. A single small-sample comparison is close to meaningless; need multiple
  runs + average (+ more questions) to make a real claim. Direct evidence for why vendor benchmark
  numbers need context.

## Progress

- ✅ Setup complete (git, venv, requirements, `.env`, key-loading test).
- ✅ Phase 1 done: `phase1.py` sends one question to **Groq** (`openai/gpt-oss-20b`), extracts the clean
  answer (`choices[0].message.content`), and handles failures with try/except. Committed.
- ✅ Phase 2 done: `phase2.py` loads my 14 BMW questions from `questions.json`, loops, asks the model
  each one (prompt ends "Answer with ONLY the letter"), grades against my answer key, prints a score.
  First run: **12/14 (85.7%)**.

## Phase 2 decisions & lessons

- **Domain: BMW cars** (something I know), so I can trust my own answer key.
- **Grader is simple:** take the first letter the model returns and compare to my `correct` letter.
  Works because the model reliably replied with just a letter. Harder parsing is Phase 5.
- **Big lesson from my own score:** the 2 the model got "wrong" (Q8 S65 engine, Q10 smallest US chassis)
  are my 2 *shakiest* questions — Q8 has two arguably-true options, Q10's answer is contested (1 vs 2
  Series). So **85.7% partly measures MY question quality, not just the model.** A benchmark score is
  entangled with the test itself.
- **To explore in Phase 7:** small sample (14 Qs → each is ~7%); and models are non-deterministic, so
  re-running may change the score with no code change.

## Experiment: same eval, 3 runs, nothing changed (Phase 7 evidence)

Ran `phase2.py` three times with zero changes on `openai/gpt-oss-20b`:
- Run 1: **12/14 (85.7%)** — wrong: Q8, Q10
- Run 2: **12/14 (85.7%)** — wrong: Q8, Q10
- Run 3: **11/14 (78.6%)** — wrong: Q8, Q10, **Q13**

Findings:
- **Non-determinism is real but selective.** Confident questions gave the same answer every run; the
  one that flipped (Q13, the nuanced logo question) is where the model is least sure. Variance appears
  where confidence is low.
- **Q8 and Q10 were wrong every run = systematic** (question/key quality), not luck.
- **A single score is falsely precise.** 14 questions → one flip = ~7 points. Honest summary of this
  model on my set is "~79–86%, depends on the run," NOT "85.7%."
- **Takeaway:** to characterize a model I'd need more questions (each matters less) + multiple runs
  (to see the spread), then report an average/range — not one number. This is *why* "Model A scored
  87%" is close to meaningless without context.
