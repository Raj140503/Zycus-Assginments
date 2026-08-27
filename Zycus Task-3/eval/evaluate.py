import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CASES_FILE = Path(__file__).resolve().parent / "test_cases.json"
RESULTS_DIR = BASE_DIR / "results"
PREDICTIONS_FILE = RESULTS_DIR / "task3_predictions.json"


if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def load_cases():
    with CASES_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_data():
    with (BASE_DIR / "data" / "accounts.json").open(
        "r", encoding="utf-8"
    ) as file:
        accounts = json.load(file)

    with (BASE_DIR / "data" / "tickets.json").open(
        "r", encoding="utf-8"
    ) as file:
        tickets = json.load(file)

    return accounts, tickets


def to_dict(result):
    """
    Convert Pydantic model / dictionary into a normal dictionary.
    """

    if hasattr(result, "model_dump"):
        return result.model_dump()

    if isinstance(result, dict):
        return result

    raise TypeError(
        f"Unsupported result type: {type(result)}"
    )


def sentence_count(text):
    return len(
        [
            sentence
            for sentence in text.split(".")
            if sentence.strip()
        ]
    )


def text_contains(value, options):
    value = str(value).lower()

    return any(
        option.lower() in value
        for option in options
    )


# =========================================================
# TASK 1
# =========================================================

def run_task1_case(case):

    from task1_triage import triage_ticket

    result = triage_ticket(
        case["subject"],
        case["body"]
    )

    output = to_dict(result)

    checks = []

    acceptance = case["acceptance"]

    # Required fields
    for field in acceptance["required_fields"]:

        checks.append(
            {
                "check": f"required field: {field}",
                "passed": (
                    field in output
                    and output[field] not in (None, "")
                ),
            }
        )

    # Product area
    checks.append(
        {
            "check": "product area",
            "passed": text_contains(
                output.get("product_area", ""),
                acceptance["product_area_contains"]
            ),
        }
    )

    # Issue category
    checks.append(
        {
            "check": "issue category",
            "passed": text_contains(
                output.get("issue_category", ""),
                acceptance["issue_category_contains"]
            ),
        }
    )

    # Urgency
    checks.append(
        {
            "check": "urgency",
            "passed": (
                output.get("urgency")
                in acceptance["urgency_in"]
            ),
        }
    )

    passed_checks = sum(
        check["passed"]
        for check in checks
    )

    quality_score = (
        passed_checks / len(checks)
        if checks
        else 0.0
    )

    return {
        "id": case["id"],
        "task": "task1",
        "adversarial": acceptance.get(
            "adversarial",
            False
        ),
        "passed": quality_score == 1.0,
        "quality_score": round(
            quality_score,
            3
        ),
        "checks": checks,
        "output": output,
    }


# =========================================================
# TASK 2
# =========================================================

def run_task2_case(case):

    from task2_account_health import (
        generate_account_health
    )

    accounts, tickets = load_data()

    account = next(
        (
            account
            for account in accounts
            if account.get("account_id")
            == case["account_id"]
        ),
        None
    )

    if account is None:
        raise ValueError(
            f"Account '{case['account_id']}' "
            "does not exist in accounts.json."
        )

    result = generate_account_health(
        case["account_id"]
    )

    output = to_dict(result)

    checks = []

    acceptance = case["acceptance"]

    # Required top-level fields
    for field in acceptance[
        "required_top_level_fields"
    ]:

        checks.append(
            {
                "check": f"required field: {field}",
                "passed": field in output,
            }
        )

    # Executive summary sentence count
    summary = output.get(
        "executive_summary",
        ""
    )

    count = sentence_count(summary)

    checks.append(
        {
            "check": "executive summary sentence count",
            "passed": (
                acceptance[
                    "summary_sentences_min"
                ]
                <= count
                <= acceptance[
                    "summary_sentences_max"
                ]
            ),
        }
    )

    # Company represented
    checks.append(
        {
            "check": "account company represented",
            "passed": text_contains(
                summary,
                acceptance[
                    "company_contains"
                ]
            ),
        }
    )

    # Direct ticket quote validation
    if acceptance.get(
        "risks_require_verbatim_ticket_quotes"
    ):

        account_tickets = {
            ticket.get("ticket_id"): ticket
            for ticket in tickets
            if ticket.get("account_id")
            == case["account_id"]
        }

        quote_checks = []

        for risk in output.get(
            "open_risks_and_flagged_issues",
            []
        ):

            ticket = account_tickets.get(
                risk.get("ticket_id")
            )

            quote_checks.append(
                bool(
                    ticket
                    and risk.get("direct_quote")
                    and risk["direct_quote"]
                    in ticket.get("body", "")
                )
            )

        checks.append(
            {
                "check": (
                    "every risk has a "
                    "verbatim ticket quote"
                ),
                "passed": (
                    all(quote_checks)
                    if quote_checks
                    else True
                ),
            }
        )

    # Talking points
    checks.append(
        {
            "check": (
                "recommended talking "
                "points present"
            ),
            "passed": bool(
                output.get(
                    "recommended_talking_points"
                )
            ),
        }
    )

    passed_checks = sum(
        check["passed"]
        for check in checks
    )

    quality_score = (
        passed_checks / len(checks)
        if checks
        else 0.0
    )

    return {
        "id": case["id"],
        "task": "task2",
        "account_id": case["account_id"],
        "company": account.get(
            "company"
        ),
        "adversarial": acceptance.get(
            "adversarial",
            False
        ),
        "passed": quality_score == 1.0,
        "quality_score": round(
            quality_score,
            3
        ),
        "checks": checks,
        "output": output,
    }


# =========================================================
# SAVE / LOAD PREDICTIONS
# =========================================================

def save_predictions(results):
    RESULTS_DIR.mkdir(exist_ok=True)

    existing_results = []

    if PREDICTIONS_FILE.exists():
        with PREDICTIONS_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:
            existing_results = json.load(file).get(
                "results",
                []
            )

    # Merge new results with existing results.
    # If the same test ID exists, replace it.
    merged = {
        result["id"]: result
        for result in existing_results
    }

    for result in results:
        merged[result["id"]] = result

    final_results = list(merged.values())

    payload = {
        "generated_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        "results": final_results,
    }

    with PREDICTIONS_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False
        )


def load_predictions():

    if not PREDICTIONS_FILE.exists():

        raise FileNotFoundError(
            "No saved predictions found. "
            "Run the evaluation with --mode generate first."
        )

    with PREDICTIONS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)["results"]


# =========================================================
# REPORT
# =========================================================

def write_report(results):

    RESULTS_DIR.mkdir(
        exist_ok=True
    )

    total = len(results)

    passed = sum(
        result["passed"]
        for result in results
    )

    average_score = (
        sum(
            result["quality_score"]
            for result in results
        ) / total
        if total
        else 0.0
    )

    report_lines = [
        "# Task 3 Evaluation Report",
        "",
        "## Summary",
        "",
        f"- Total test cases: {total}",
        f"- Passed test cases: {passed}",
        f"- Failed test cases: {total - passed}",
        f"- Average quality score: {average_score:.3f}",
        "",
        "## Test Results",
        "",
        "| Test | Task | Adversarial | Result | Score |",
        "|---|---|---|---|---:|",
    ]

    for result in results:

        report_lines.append(
            f"| {result['id']} "
            f"| {result['task']} "
            f"| {'Yes' if result['adversarial'] else 'No'} "
            f"| {'PASS' if result['passed'] else 'FAIL'} "
            f"| {result['quality_score']:.3f} |"
        )

    report_lines.extend(
        [
            "",
            "## Methodology",
            "",
            "The evaluation uses acceptance-criteria test cases "
            "covering both Task 1 and Task 2.",
            "",
            "Each case is evaluated using deterministic checks "
            "against the structured agent output.",
            "",
            "Task 1 checks required fields, product area, "
            "issue category, and urgency.",
            "",
            "Task 2 checks required sections, executive-summary "
            "length, account identity, verbatim ticket quotes "
            "for risks, and recommended talking points.",
            "",
            "One adversarial case is included for each task.",
            "",
            "The evaluation results are saved after the LLM "
            "calls so the report can be regenerated without "
            "making additional API calls.",
        ]
    )

    report_path = (
        RESULTS_DIR /
        "task3_report.md"
    )

    report_path.write_text(
        "\n".join(report_lines)
        + "\n",
        encoding="utf-8"
    )

    json_path = (
        RESULTS_DIR /
        "task3_results.json"
    )

    with json_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "total_cases": total,
                "passed_cases": passed,
                "failed_cases": total - passed,
                "average_quality_score": round(
                    average_score,
                    3
                ),
                "results": results,
            },
            file,
            indent=2,
            ensure_ascii=False
        )


# =========================================================
# MAIN
# =========================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--task",
        choices=[
            "task1",
            "task2",
            "all"
        ],
        default="all"
    )

    parser.add_argument(
        "--mode",
        choices=[
            "generate",
            "report"
        ],
        default="report"
    )

    args = parser.parse_args()

    # -----------------------------------------------------
    # REPORT MODE
    # -----------------------------------------------------

    if args.mode == "report":

        results = load_predictions()

        write_report(results)

        print()
        print(
            "Report generated from saved predictions."
        )
        print(
            "Report: results/task3_report.md"
        )
        print(
            "JSON:   results/task3_results.json"
        )

        return

    # -----------------------------------------------------
    # GENERATE MODE
    # -----------------------------------------------------

    cases = load_cases()

    selected_cases = []

    if args.task in (
        "task1",
        "all"
    ):

        selected_cases.extend(
            cases["task1"]
        )

    if args.task in (
        "task2",
        "all"
    ):

        selected_cases.extend(
            cases["task2"]
        )

    results = []

    for case in selected_cases:

        print(
            f"Running {case['id']}..."
        )

        try:

            if case["task"] == "task1":

                result = run_task1_case(
                    case
                )

            else:

                result = run_task2_case(
                    case
                )

            results.append(result)

            print(
                f"  "
                f"{'PASS' if result['passed'] else 'FAIL'} "
                f"score="
                f"{result['quality_score']:.3f}"
            )

        except Exception as error:

            result = {
                "id": case["id"],
                "task": case["task"],
                "adversarial": case[
                    "acceptance"
                ].get(
                    "adversarial",
                    False
                ),
                "passed": False,
                "quality_score": 0.0,
                "checks": [
                    {
                        "check": "execution",
                        "passed": False,
                        "error": str(error),
                    }
                ],
                "output": None,
            }

            results.append(result)

            print(
                f"  FAIL execution: {error}"
            )

    save_predictions(results)

    write_report(results)

    print()
    print(
        "Evaluation complete."
    )

    print(
        "Saved predictions: "
        "results/task3_predictions.json"
    )

    print(
        "Report: results/task3_report.md"
    )

    print(
        "JSON: results/task3_results.json"
    )


if __name__ == "__main__":
    main()
