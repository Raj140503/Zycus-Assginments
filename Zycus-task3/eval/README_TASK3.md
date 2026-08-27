# Task 3 — Evaluation Harness

This folder implements the Task 3 evaluation harness for both Task 1 and Task 2.

## Coverage

- 5 Task 1 test cases
- 5 Task 2 test cases
- 1 adversarial case per task
- Deterministic rule-based acceptance checks
- Pass/fail per test
- Quality score from 0 to 1 per test
- JSON and Markdown summary reports

## Where to place it

For the final combined repository, place this `eval/` folder at the repository root beside:

```text
task1_triage.py
task2_account_health.py
data/
knowledge-base/
```

## Install

Add/install:

```powershell
python -m pip install scikit-learn
```

The harness itself uses deterministic acceptance checks; it does not add a second LLM judge.

## Run

From the final combined repository root:

```powershell
python eval/evaluate_task3.py --task all
```

Or run only one task:

```powershell
python eval/evaluate_task3.py --task task1
python eval/evaluate_task3.py --task task2
```

Reports are written to:

```text
results/task3_report.md
results/task3_results.json
```

## Important

The harness calls the real Task 1 and Task 2 agents. Running it therefore uses the configured Gemini API key and consumes API quota.
