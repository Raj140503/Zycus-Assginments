import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Add it to the .env file."
    )

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


class RiskFlag(BaseModel):
    issue: str = Field(
        description="The risk or escalation issue identified."
    )
    reason: str = Field(
        description="Why this issue represents a risk or escalation signal."
    )
    ticket_id: str = Field(
        description="Ticket ID supporting the risk."
    )
    direct_quote: str = Field(
        description="Direct quote copied from the supporting ticket."
    )


class AccountHealthOutput(BaseModel):
    executive_summary: str = Field(
        description="Executive summary in 3 to 5 sentences."
    )
    open_risks_and_flagged_issues: list[RiskFlag] = Field(
        description="Open risks and escalation/churn signals."
    )
    recommended_talking_points: list[str] = Field(
        description="Actionable QBR talking points for the TAM."
    )


class AccountHealthAgent:

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

        self.accounts = self._load_json(
            DATA_DIR / "accounts.json"
        )
        self.tickets = self._load_json(
            DATA_DIR / "tickets.json"
        )

    def _load_json(self, path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _get_account(self, account_id):
        for account in self.accounts:
            if account.get("account_id") == account_id:
                return account
        return None

    def _parse_ticket_date(self, ticket):
        for field in (
            "created_at",
            "created_date",
            "created",
            "date",
        ):
            value = ticket.get(field)
            if value:
                try:
                    return datetime.fromisoformat(
                        str(value).replace("Z", "+00:00")
                    )
                except ValueError:
                    pass
        return None

    def _get_recent_tickets(self, account_id):
        account_tickets = [
            ticket
            for ticket in self.tickets
            if ticket.get("account_id") == account_id
        ]

        dated_tickets = [
            (ticket, self._parse_ticket_date(ticket))
            for ticket in account_tickets
        ]

        dated_tickets = [
            (ticket, date)
            for ticket, date in dated_tickets
            if date is not None
        ]

        if not dated_tickets:
            return account_tickets

        latest_date = max(
            date for _, date in dated_tickets
        )

        cutoff = latest_date - timedelta(days=90)

        return [
            ticket
            for ticket, date in dated_tickets
            if date >= cutoff
        ]

    def _format_tickets(self, tickets):
        if not tickets:
            return "No tickets found for this account."

        formatted = []

        for ticket in tickets:
            formatted.append(
                "\n".join(
                    [
                        f"Ticket ID: {ticket.get('ticket_id', '')}",
                        f"Subject: {ticket.get('subject', '')}",
                        f"Created: {self._parse_ticket_date(ticket) or ''}",
                        f"Status: {ticket.get('status', '')}",
                        f"Urgency: {ticket.get('urgency', ticket.get('priority', ''))}",
                        f"Category: {ticket.get('category', '')}",
                        "Body:",
                        ticket.get("body", ""),
                    ]
                )
            )

        return "\n\n--------------------\n\n".join(formatted)

    def generate(self, account_id):
        account = self._get_account(account_id)

        if account is None:
            raise ValueError(
                f"Account '{account_id}' was not found."
            )

        recent_tickets = self._get_recent_tickets(
            account_id
        )

        account_context = json.dumps(
            account,
            indent=2,
            default=str
        )

        ticket_context = self._format_tickets(
            recent_tickets
        )

        prompt = f"""
You are an AI assistant supporting a Technical Account Manager (TAM).

Generate an actionable account health brief using ONLY the
supplied account information and ticket history.

Do not use external data.

ACCOUNT INFORMATION
===================

{account_context}


TICKETS FROM THE LAST 90 DAYS
=============================

{ticket_context}


OUTPUT REQUIREMENTS
===================

Produce exactly three sections.

1. EXECUTIVE SUMMARY

Write 3 to 5 concise sentences summarizing the current
account situation, important activity, and overall health.

2. OPEN RISKS & FLAGGED ISSUES

Identify tickets suggesting:
- churn risk
- escalation risk
- unresolved serious issues
- repeated customer problems
- other material account risks

Every risk must contain:
- issue
- reason
- ticket ID
- a direct quote copied from that ticket

Never invent a quote.

If there are no meaningful risks, return an empty list.

3. RECOMMENDED TALKING POINTS

Provide concise, actionable points the TAM should discuss
during the QBR.

Focus only on facts supported by the account and ticket data.

DETERMINISM
===========

Return the same result for the same input.
Do not introduce random or speculative information.
"""

        print("Generating account health brief:")
        print()

        stream = self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=AccountHealthOutput,
            ),
        )

        response_text = ""

        for chunk in stream:

            if chunk.text:
                print(
                    chunk.text,
                    end="",
                    flush=True
                )

            response_text += chunk.text

        print()
        print()

        if not response_text.strip():
            raise RuntimeError(
                "Gemini did not return a response."
        )

        try:
            result = AccountHealthOutput.model_validate_json(
                response_text
            )

        except Exception as error:
            raise RuntimeError(
                "Could not parse Gemini's streamed "
                "structured response."
            ) from error
            
        self._validate_result(
             result,
            recent_tickets
        )

        return result
    def _validate_result(self, result, tickets):
        sentence_count = len(
            [
                sentence
                for sentence in result.executive_summary.split(".")
                if sentence.strip()
            ]
        )

        if sentence_count < 3 or sentence_count > 5:
            raise ValueError(
                "Executive summary must contain 3-5 sentences."
            )

        ticket_lookup = {
            ticket.get("ticket_id"): ticket
            for ticket in tickets
        }

        for risk in result.open_risks_and_flagged_issues:
            ticket = ticket_lookup.get(risk.ticket_id)

            if ticket is None:
                raise ValueError(
                    f"Risk references unknown ticket: {risk.ticket_id}"
                )

            ticket_body = ticket.get("body", "")

            if risk.direct_quote not in ticket_body:
                raise ValueError(
                    "Risk quote was not found verbatim in "
                    f"ticket {risk.ticket_id}."
                )


def generate_account_health(account_id):
    agent = AccountHealthAgent()
    return agent.generate(account_id)


if __name__ == "__main__":
    print()
    print("===================================")
    print(" Zycus TAM Account Health Summary")
    print("===================================")
    print()

    account_id = input(
        "Enter account ID: "
    ).strip()

    print()
    print("Generating account health brief...")
    print()

    result = generate_account_health(account_id)
