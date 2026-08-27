# Task 3 - Evaluation Harness

An evaluation harness for systematically testing the Task 1 Intelligent
Ticket Triage Agent and Task 2 TAM Account Health Summary agent against
defined acceptance criteria.

## Features

- Automated evaluation of Task 1 and Task 2
- Five test cases for Task 1
- Five test cases for Task 2
- Adversarial test coverage
- Deterministic acceptance-criteria checks
- Per-test quality scores from 0 to 1
- JSON evaluation results
- Markdown evaluation report
- Saved predictions to allow report regeneration without additional LLM calls

## Project Structure

```text
Zycus-task3/
├── eval/
│   ├── evaluate_task3.py
│   ├── test_cases.json
│   └── README_TASK3.md
├── results/
│   ├── task3_predictions.json
│   ├── task3_results.json
│   ├── task3_report.md
│   └── README.md
└── requirements_task3.txt
```

## Setup

Activate the project virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the Task 3 dependencies:

```bash
pip install -r requirements_task3.txt
```

## Evaluation

Generate evaluation results for both tasks:

```bash
python eval/evaluate_task3.py --task all --mode generate
```

Evaluate only Task 1:

```bash
python eval/evaluate_task3.py --task task1 --mode generate
```

Evaluate only Task 2:

```bash
python eval/evaluate_task3.py --task task2 --mode generate
```

After predictions have been saved, regenerate the report without making
additional LLM API calls:

```bash
python eval/evaluate_task3.py --mode report
```

## Evaluation Criteria

### Task 1

The harness checks:

- Required output fields
- Product-area classification
- Issue-category classification
- Urgency / priority classification

### Task 2

The harness checks:

- Required top-level output fields
- Executive-summary sentence count
- Correct account/company representation
- Verbatim ticket quotes for identified risks
- Recommended TAM talking points

## Test Coverage

The evaluation suite contains:

- 5 Task 1 test cases
- 5 Task 2 test cases
- 1 adversarial case for Task 1
- 1 adversarial case for Task 2

## Evaluation Results

The completed evaluation produced:

- **10 total test cases**
- **8 fully passed**
- **2 partial/failing cases**
- **0.982 average quality score**
- **Task 2: 5/5 passed**
- **Task 1: 3/5 fully passed**

The two Task 1 partial cases received a quality score of 0.909 each.

These results are preserved in the `results/` directory and are intended
to provide transparent evidence of agent quality rather than artificially
optimizing the test outcomes.

## Output Files

After evaluation, the harness produces:

```text
results/
├── task3_predictions.json
├── task3_results.json
└── task3_report.md
```

`task3_predictions.json` stores the evaluated agent outputs,
`task3_results.json` stores structured scoring results, and
`task3_report.md` provides a human-readable evaluation summary.
