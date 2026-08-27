# Task 2 - TAM Account Health Summary

An AI-powered account health agent that analyzes customer account
information and related support tickets to generate an executive-ready
account health brief for Technical Account Managers (TAMs).

## Features

- Executive account summary
- Open risks and flagged issues
- Grounded analysis using account and ticket data
- Verbatim ticket-quote validation for identified risks
- Recommended TAM talking points
- Structured Pydantic output
- Streaming response generation
- Streamlit-based user interface

## Project Structure

```text
Zycus_task2/
├── account_health.py
├── app.py
├── data/
│   ├── accounts.json
│   └── tickets.json
├── knowledge-base/
│   ├── billing/
│   ├── onboarding/
│   ├── products/
│   └── troubleshooting/
├── requirements.txt
└── .env.example
```

## Setup

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file using `.env.example` as a template:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Do not commit the real `.env` file or API key to GitHub.**

## Run

### Command Line

```bash
python account_health.py
```

The application prompts for an account ID and generates an account-health
brief using the account and related support-ticket data.

### Streamlit UI

```bash
streamlit run app.py
```

The Streamlit interface provides a user-friendly way to enter an account ID
and view the generated account-health summary.

## Account Health Output

The agent generates:

- `executive_summary`
- `open_risks_and_flagged_issues`
- `recommended_talking_points`

For identified risks, the output can include:

- Issue
- Reason
- Ticket ID
- Direct quote from the source ticket

## Data Grounding

The agent uses the supplied account and ticket data to generate the health
brief. Risk references are validated against the underlying ticket data so
that quoted ticket text is grounded in the source record.

## Streaming

Streaming generation is implemented so that the account-health response can
be produced incrementally, improving perceived responsiveness during model
generation.

## Example

```text
Account ID:
ACC-3336
```

The agent generates an executive summary, open risks and flagged issues,
and recommended talking points for the selected customer account.
