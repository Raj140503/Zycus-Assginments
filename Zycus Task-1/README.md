# Task 1 - Intelligent Ticket Triage Agent

An AI-powered support ticket triage agent that analyzes incoming support
tickets and produces a structured triage response.

## Features

- Product-area classification
- Issue-category classification
- Urgency / priority classification
- Knowledge-base retrieval
- Known-issue detection
- Recommended responder team
- Draft first response
- Structured Pydantic output
- Streaming response generation

## Project Structure

```text
Zycus Task-1/
├── triage.py
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

```bash
python triage.py
```

The application prompts for:

1. Ticket subject
2. Ticket body

It then analyzes the ticket and returns a structured triage result.

## Triage Output

The agent generates:

- `product_area`
- `issue_category`
- `urgency`
- `reasoning`
- `known_issue`
- `relevant_kb_document`
- `recommended_responder_team`
- `draft_first_response`

## Knowledge Base

The agent uses the supplied Markdown knowledge base to retrieve relevant
product and troubleshooting context before generating the final triage
response.

## Streaming

Streaming generation is implemented to provide incremental model output
while the triage response is being generated.

## Example

**Input**

```text
Subject:
Login failure

Body:
Users are unable to log in to the application. The login page keeps
rejecting valid credentials.
```

**Output**

The agent returns a structured JSON response containing the detected
product area, issue category, urgency, knowledge-base context,
recommended responder team, and a draft first response.
