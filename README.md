# Zycus AI Engineering Assignment

This repository contains my implementation of the Zycus AI Engineering Assignment.

## Tasks

### Task 1 - Intelligent Ticket Triage Agent

An AI-powered support ticket triage agent that analyzes incoming support tickets and produces a structured triage response.

Key capabilities:
- Product-area classification
- Issue-category classification
- Urgency / priority classification
- Knowledge-base retrieval
- Known-issue detection
- Recommended responder team
- Draft first response
- Structured Pydantic output
- Streaming response generation

**Implementation:** `Zycus Task-1/`

### Task 2 - TAM Account Health Summary

An AI-powered account health agent that analyzes customer account information and related support tickets to generate an executive-ready account health brief.

Key capabilities:
- Executive account summary
- Open risks and flagged issues
- Verbatim ticket-quote grounding
- Recommended TAM talking points
- Streaming generation
- Streamlit-based interface

**Implementation:** `Zycus_task2/`

### Task 3 - Evaluation Harness

An evaluation framework for testing the Task 1 and Task 2 agents against structured acceptance criteria.

Current evaluation:
- 10 test cases
- 8 fully passed
- Average quality score: 0.982
- 1 adversarial test case for each task

**Implementation:** `Zycus-task3/`

### Task 4 - Production Design Note

A production-oriented design note covering:
- Failure modes and mitigation
- Latency vs. quality trade-offs
- Data sensitivity and security
- Scaling considerations at 10× volume

**Implementation:** `DESIGN_NOTE_TASK4.md`

## Technology

- Python
- Google Gemini API
- Pydantic
- Streamlit
- JSON
- Markdown knowledge base

## Security

API credentials are loaded through environment variables.

The real `.env` file and virtual environments are excluded from version control. Use `.env.example` as the configuration template.

## Repository Structure

```text
Zycus-Assginments/
├── README.md
├── Zycus Task-1/
├── Zycus_task2/
├── Zycus-task3/
└── DESIGN_NOTE_TASK4.md
```
