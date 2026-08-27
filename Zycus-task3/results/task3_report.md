# Task 3 Evaluation Report

## Summary

- Total test cases: 10
- Passed test cases: 8
- Failed test cases: 2
- Average quality score: 0.982

## Test Results

| Test | Task | Adversarial | Result | Score |
|---|---|---|---|---:|
| T2-01 | task2 | No | PASS | 1.000 |
| T2-02 | task2 | No | PASS | 1.000 |
| T2-03 | task2 | No | PASS | 1.000 |
| T2-04 | task2 | No | PASS | 1.000 |
| T2-05 | task2 | Yes | PASS | 1.000 |
| T1-01 | task1 | No | PASS | 1.000 |
| T1-02 | task1 | No | PASS | 1.000 |
| T1-03 | task1 | No | FAIL | 0.909 |
| T1-04 | task1 | No | FAIL | 0.909 |
| T1-05 | task1 | Yes | PASS | 1.000 |

## Methodology

The evaluation uses acceptance-criteria test cases covering both Task 1 and Task 2.

Each case is evaluated using deterministic checks against the structured agent output.

Task 1 checks required fields, product area, issue category, and urgency.

Task 2 checks required sections, executive-summary length, account identity, verbatim ticket quotes for risks, and recommended talking points.

One adversarial case is included for each task.

The evaluation results are saved after the LLM calls so the report can be regenerated without making additional API calls.
