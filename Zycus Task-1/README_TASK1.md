# Task 1 — Intelligent Ticket Triage Agent

This implementation accepts a raw support ticket as text or as JSON/dict with `subject` and `body` and returns a structured triage result.

## Run

```bash
pip install -r requirements.txt
```

Set `OPENAI_API_KEY` in the environment. Do not commit the real key.

Example:

```bash
python -m task1_triage --subject "Pipeline stopped" --body "Our production pipeline has stopped processing records."
```

## Python callable

```python
from task1_triage import triage_ticket

result = triage_ticket({
    "subject": "Pipeline stopped",
    "body": "Our production pipeline has stopped processing records."
})
```

## Retrieval

The supplied Markdown knowledge base is split on horizontal-rule section boundaries (`---`) and headings are retained as retrieval metadata. Local TF-IDF retrieval supplies the most relevant KB sections to the LLM.

## Structured output

The LLM output is parsed into a Pydantic `TriageOutput` model and validated against the product-area, category, and urgency values present in the supplied dataset.
