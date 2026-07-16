# 📒 My Model Evaluation Harness — Cheat Sheet

> **What this is:** my personal "I'm confused, help me" document. Whenever I forget what I'm
> doing or why, I open this. Plain English, no jargon left unexplained. Claude keeps it updated
> as we go.
>
> _Last updated: Phase 1 in progress — switched from Anthropic to a free provider (Gemini), first
> call worked once, then Gemini's free tier got flaky. Considering Groq as a more reliable primary._

---

## 🆘 If I'm lost RIGHT NOW, start here

I closed my terminal, so my workspace went to sleep. To wake it back up, open **Terminal** and run:

```
cd ~/Desktop/"Model Evaluation Harness"
source venv/bin/activate
```

I know it worked when I see **`(venv)`** at the start of my prompt line. That's my "I'm inside my
project's sandbox" signal. If I don't see it, my libraries won't be found and nothing works right.

(The quotes around "Model Evaluation Harness" matter — the folder name has spaces, and without
quotes the terminal gets confused.)

---

## 🎯 What I'm building (in one breath)

A command-line tool that gives a set of AI models the **same exam**, grades their answers, and
prints a **scorecard** showing who did best and how much it cost. I build it in 7 small phases so
it always works and just does more each week.

The secret deeper goal: by the end I should be able to explain why a model scoring "87%" is often
*meaningless* without more context. The tool is how I earn that insight.

---

## 🤝 How Claude and I work

Claude is my **tutor, not my code-writer**. It explains things and shows small examples, but **I
type my own project code** and should be able to explain every line. That's the whole point — if I
let it write everything, I'd have a working tool and an empty head.

---

## 📖 Glossary (words that keep coming up)

| Word | What it actually means |
|------|------------------------|
| **CLI / terminal** | The text window where I type commands instead of clicking buttons. |
| **git** | A "save-point" system. Every *commit* is a snapshot I can return to. |
| **repo (repository)** | The folder git is tracking, with all its history. |
| **commit** | One saved snapshot, with a note describing what changed. |
| **virtual environment (venv)** | A private sandbox for THIS project's Python libraries, so they don't collide with the rest of my computer. The proper name (not "sandbox"). |
| **pip** | Python's tool for installing libraries from the internet. |
| **library / package** | Pre-written code I can use so I don't build everything from scratch. |
| **requirements.txt** | The "recipe" listing exactly which libraries + versions I installed. |
| **.env** | A hidden file holding secrets (like my API key). Never goes into git. |
| **.gitignore** | A list telling git which files to pretend don't exist (like `.env`). |
| **API key** | A secret password that proves I'm allowed to use the AI model's service. |

---

## 🪜 Everything I've done, step by step

### Step 1 — Checked my Python version
```
python3 --version
```
**What it does:** prints which Python I have (mine: 3.14.5).
**Why:** the project needs Python 3.11 or newer. Building on an old version causes confusing
errors later. Check the foundation first.

### Step 2 — Started a git repo
```
git init
```
**What it does:** turns my project folder into something git tracks.
**Why:** so I get save-points (commits) and can see exactly what changed when something breaks.

### Step 3 — Created a `.gitignore` file (BEFORE committing)
A file listing things git should ignore: `.env`, `venv/`, Python cache files.
**Why, and why first:** the big one is `.env`, which will hold my secret API key. A key committed
to git is leaked **forever** (git remembers history). I set this up before the key existed so there
was never a chance for it to slip in.

### Step 4 — Made my first commit
```
git add .
git status
git commit -m "Initial setup: gitignore and project spec"
```
**What it does:** `add` stages files, `status` lets me SEE what's about to be saved, `commit` saves
the snapshot.
**Why the `status` step:** never save blind. I check that `.env` and `venv` are NOT in the list.
That checking habit is the actual skill.

### Step 5 — Created + activated my virtual environment
```
python3 -m venv venv
source venv/bin/activate
```
**What it does:** builds a private Python sandbox in a folder called `venv`, then turns it on
(prompt shows `(venv)`).
**Why:** keeps this project's libraries walled off from my Mac's shared system Python so nothing
collides or breaks.
**Gotcha:** activation only lasts for that terminal window. New window = activate again.

### Step 6 — Installed libraries + froze the list
```
pip install requests python-dotenv
pip freeze > requirements.txt
```
**What it does:** installs two helper libraries, then writes the exact installed list into
`requirements.txt`.
**The two libraries:**
- `requests` → makes HTTP calls (how I'll talk to the AI model's API).
- `python-dotenv` → reads my `.env` file so my code can use the key without hardcoding it.
**Why `requirements.txt` matters:** it's the recipe to rebuild this exact setup on any computer.
That's why I can safely ignore the big `venv/` folder in git — the recipe is saved, the bulky
ingredients aren't.

### Step 7 — Created `.env` and proved my code can read the key
```
echo 'ANTHROPIC_API_KEY=placeholder-will-swap-real-key-later' > .env
cat .env
```
**What it does:** `echo ... > .env` writes the key line into the hidden `.env` file in one shot;
`cat .env` reads it back to confirm.
**Why `echo >` instead of nano:** nano kept closing before I saved, leaving the file empty. `echo`
writes AND saves in one command — no editor to trip over.

Then I wrote my first Python file, `check_env.py`, to prove the key loads:
```python
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("ANTHROPIC_API_KEY")

if key:
    print("Key loaded! Length:", len(key), "characters")
else:
    print("No key found — check your .env file")
```
Ran it with `python check_env.py` → printed `Key loaded! Length: 36 characters`. That proves the
chain works: `.env` → dotenv → my code. It prints the *length*, never the key itself (safe habit).
**Python gotcha:** the lines under `if`/`else` MUST be indented (4 spaces) — that's how Python knows
what belongs to what.

**My environment "on paper" right now:**
```
certifi==2026.5.20
charset-normalizer==3.4.7
idna==3.18
python-dotenv==1.2.2
requests==2.34.2
urllib3==2.7.0
```
(I installed `requests` and `python-dotenv` directly; the other 4 came along as their dependencies.)

---

## ⚡ Commands I'll type a lot (quick reference)

| Command | What it does |
|---------|--------------|
| `cd ~/Desktop/"Model Evaluation Harness"` | Go to my project folder. |
| `source venv/bin/activate` | Turn on my virtual environment. |
| `ls -a` | List all files, including hidden ones (like `.env`, `.gitignore`). |
| `cat filename` | Print a file's contents to the screen. |
| `git status` | See what's changed / about to be saved. |
| `git add .` | Stage all my changes for the next commit. |
| `git commit -m "message"` | Save a snapshot with a note. |
| `pip freeze` | Show all installed libraries + versions. |

---

## 🔀 Big direction change (from Nick)

Nick redirected the project. Key points:
- Build around the **OpenAI API standard chat endpoint** (`/v1/chat/completions`) — the request/response
  format most providers copied. Send `model` + a `messages` list; read the answer from
  `choices[0].message.content`.
- Stay **provider-agnostic**: switching providers = change only 3 things — **base URL, API key, model name**.
- **Don't eval Anthropic** models (already benchmarked to death) — use free, non-Anthropic models.
- **Find free providers myself** (the point is the exercise). Free + OpenAI-compatible options: Groq,
  Cerebras, Google Gemini, OpenRouter, NVIDIA NIM, GitHub Models.
- The `.env` variable name is whatever I code it to be — not fixed. Renamed mine to `GEMINI_API_KEY`.
- Lesson: Claude leaned toward Anthropic because it's made by Anthropic — a **bias**. Distrusting model
  output like that is the whole point of the project.

## Step 8 — Switched to Google Gemini + made my first real API call
- Got a free Gemini key at aistudio.google.com (Free tier, no card), stored as `GEMINI_API_KEY` in `.env`.
- Updated `check_env.py` to read `GEMINI_API_KEY` (one-word edit) — confirmed it loads (53 chars).
- Wrote `phase1.py` using `requests` to POST to Gemini's OpenAI-compatible endpoint:
  `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions`, header
  `Authorization: Bearer <key>`, body with `model` + `messages`.
- It WORKED once — returned "The capital of France is Paris." That proves the code is correct.

## 📍 Where I am right now

**✅ Phase 1 done** — `phase1.py` calls Groq (`openai/gpt-oss-20b`), extracts the clean answer, handles
failures. Switched to Groq after Gemini's free tier kept throwing `404`/`503`.

**✅ Phase 2 done** — `phase2.py` loads 14 BMW questions from `questions.json`, asks the model each,
grades against my answer key, prints a score. First run: **12/14 (85.7%)**. Key insight: both misses
were on my shakiest questions, so the score partly reflects MY question quality, not just the model.

**Next → Phase 3:** make it config-driven so adding a 2nd model is a config edit, not a code change —
which sets up actually comparing models.

---

## 🧱 Gotchas I've hit (so I don't repeat them)

- Folder name has spaces → wrap it in quotes: `cd ~/Desktop/"Model Evaluation Harness"`.
- Closing the terminal turns off the venv → re-run `source venv/bin/activate`.
- A stray `'` in the terminal makes it wait for a closing quote → press **Ctrl+C** to cancel.
- "Sandbox" was just my nickname for it; the real term is **virtual environment**.
- Never put a real API key anywhere except `.env`.
- `cat.env` fails — needs a space: `cat .env` (command and filename are separate words).
- Typing `NAME=value` at the shell prompt sets a temporary variable; it does NOT save to a file.
- nano: I must wait for the editor screen (with `^O ^X` at the bottom) before typing, or nothing saves.
- Python indentation is required, not decoration — lines under `if`/`else` need 4 spaces.
- Mismatched quotes (`"..'`) make the terminal show `dquote>` — press Ctrl+C, redo with matching quotes.
- API status codes: `200` = success, `404` = model/URL not found (often a deprecated model name),
  `503` = server overloaded (temporary — just retry). Always print and read the status code.
- Model names get retired FAST. Verify against the provider's live models page before trusting one.
  Pin an exact model name (not a "latest" alias) so eval runs stay reproducible.
- A `503` is a "transient error" — Phase 4 (retry with backoff) is literally built to auto-handle these.
