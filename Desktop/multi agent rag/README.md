# Phase 4 — Memory, Evaluation & Observability

Three new features this phase. Follow the steps in order.

---

## What's new

| Feature | File | What it does |
|---|---|---|
| F10 Memory | `src/state.py`, `src/agents/supervisor.py`, `src/agents/generate.py`, `main.py` | Remembers previous questions in the same session |
| F11 Evaluation | `src/evaluate.py`, `data/eval_questions.json` | Automatically scores the system on 5 test questions |
| F12 Observability | `src/config.py` + Langfuse account | Dashboard showing every agent call, timing, and cost |

---

## Step 1 — Copy the files into your project

Unzip this package and drag everything into your `multi agent rag` folder,
overwriting files with the same name. New files added:
```
src/evaluate.py
data/eval_questions.json
tests/test_memory.py
```

Updated files (overwrite these):
```
src/state.py
src/config.py
src/agents/supervisor.py
src/agents/generate.py
main.py
requirements.txt
.env.example
```

---

## Step 2 — Install the new package

```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## Step 3 — Test memory (Feature 10)

```bash
.venv\Scripts\python.exe -m tests.test_memory
```

You should see it answer "How many customers have churned?" and then
correctly answer "Why did they leave?" — proving it understood the
follow-up without you repeating yourself.

Then try it yourself in the real chat:
```bash
.venv\Scripts\python.exe -m main
```
Type: `How many customers have churned?`
Then type: `Why did they leave?`
Then type: `Which plan had the most?`

Each answer should build on the previous one naturally.

---

## Step 4 — Run the evaluation (Feature 11)

```bash
.venv\Scripts\python.exe -m src.evaluate
```

This runs 5 test questions automatically and scores the system. You'll
see output like:

```
[Q1] How many customers have churned?
  ✅ PASS | keywords 100% | agents 100% | critic=ok | 3.2s

[Q2] Why did customers churn last quarter?
  ✅ PASS | keywords 100% | agents 100% | critic=ok | 4.1s
...

SUMMARY
  Keyword score:    95.0%
  Agent routing:    90.0%
  Critic pass rate: 100.0%

Full results saved to data/eval_results.json
```

The full results are saved to `data/eval_results.json` — open it to see
every question, answer, and score. Run it again after any change to see
if the scores improved or got worse.

---

## Step 5 — Set up observability (Feature 12, optional but recommended)

This gives you a live dashboard to see every agent call.

1. Go to **[cloud.langfuse.com](https://cloud.langfuse.com)** and sign up free
2. Create a new project (call it "multi-agent-analyst")
3. Go to **Settings → API Keys → Create new key**
4. Copy both the **Public Key** and **Secret Key**
5. Open your `.env` file and add them:
```
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
```
6. Run the app:
```bash
.venv\Scripts\python.exe -m main
```
7. Ask a question, then go to your Langfuse dashboard — you'll see
   every agent call listed with timing and the exact prompt/response.

If you skip this step, everything still works — Langfuse is optional.

---

## Troubleshooting

- **Memory test FAIL** — make sure you copied the updated `supervisor.py`,
  `generate.py`, `state.py`, and `main.py` — all four need the chat_history changes.
- **Evaluation hangs** — it makes 5 × 5 API calls. If quota runs out
  mid-run, wait and try again tomorrow.
- **Langfuse "package not installed"** — run:
  `.venv\Scripts\python.exe -m pip install langfuse`

---

## What's next — Phase 5 (Backend)

Once this phase passes, we build the **FastAPI backend** — a proper API
server so a website can talk to the AI. That's the bridge between the
AI brain you've built and the frontend (the actual website).

Come back once Steps 3 and 4 are passing!
 