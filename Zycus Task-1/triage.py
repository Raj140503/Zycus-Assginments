import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. "
        "Add it to the .env file."
    )


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
KB_DIR = BASE_DIR / "knowledge-base"


# ---------------------------------------------------------
# Allowed values from the assignment dataset
# ---------------------------------------------------------

ALLOWED_CATEGORIES = [
    "Bug",
    "Feature Request",
    "How-To",
    "Performance",
    "Billing",
    "Integration",
    "Onboarding",
    "Data Loss",
]

ALLOWED_URGENCY = [
    "P1",
    "P2",
    "P3",
    "P4",
]


# ---------------------------------------------------------
# Structured output
# ---------------------------------------------------------

class TriageOutput(BaseModel):

    product_area: str = Field(
        description="Product area associated with the ticket."
    )

    issue_category: str = Field(
        description="Issue category of the ticket."
    )

    urgency: str = Field(
        description="Urgency tier. Must be P1, P2, P3, or P4."
    )

    reasoning: str = Field(
        description="Reasoning for the classification and urgency."
    )

    known_issue: bool = Field(
        description=(
            "Whether the ticket matches a known issue "
            "described in the knowledge base."
        )
    )

    relevant_kb_document: str = Field(
        description=(
            "Most relevant knowledge-base document "
            "for the ticket."
        )
    )

    recommended_responder_team: str = Field(
        description="Recommended responder team."
    )

    draft_first_response: str = Field(
        description=(
            "Draft first-response message that a support "
            "agent can send to the customer."
        )
    )


# ---------------------------------------------------------
# Knowledge Base Retrieval
# ---------------------------------------------------------

class KnowledgeBaseRetriever:

    def __init__(self, kb_directory):

        self.kb_directory = Path(kb_directory)

        self.documents = self._load_documents()

        if not self.documents:
            raise ValueError(
                "No knowledge-base Markdown documents found."
            )

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2)
        )

        self.document_matrix = self.vectorizer.fit_transform(
            [
                document["content"]
                for document in self.documents
            ]
        )

    def _load_documents(self):

        documents = []

        for file_path in sorted(
            self.kb_directory.rglob("*.md")
        ):

            content = file_path.read_text(
                encoding="utf-8"
            )

            # The supplied starter data uses "---"
            # as knowledge-base section separators.
            sections = re.split(
                r"\n\s*---\s*\n",
                content
            )

            for section in sections:

                section = section.strip()

                if not section:
                    continue

                headings = re.findall(
                    r"^#{1,6}\s+(.+)$",
                    section,
                    flags=re.MULTILINE
                )

                heading = " > ".join(headings)

                documents.append(
                    {
                        "document": str(
                            file_path.relative_to(
                                BASE_DIR
                            )
                        ),
                        "heading": heading,
                        "content": section
                    }
                )

        return documents

    def search(
        self,
        query,
        top_k=4
    ):

        query_vector = self.vectorizer.transform(
            [query]
        )

        scores = cosine_similarity(
            query_vector,
            self.document_matrix
        )[0]

        ranked_indices = scores.argsort()[::-1][:top_k]

        results = []

        for index in ranked_indices:

            document = self.documents[index]

            results.append(
                {
                    "document": document["document"],
                    "heading": document["heading"],
                    "content": document["content"],
                    "score": round(
                        float(scores[index]),
                        4
                    )
                }
            )

        return results


# ---------------------------------------------------------
# Ticket Triage Agent
# ---------------------------------------------------------

class TicketTriageAgent:

    def __init__(self):

        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        self.model = GEMINI_MODEL

        self.retriever = KnowledgeBaseRetriever(
            KB_DIR
        )

        self.product_areas = (
            self._load_product_areas()
        )

    # -----------------------------------------------------
    # Load product areas from supplied ticket dataset
    # -----------------------------------------------------

    def _load_product_areas(self):

        tickets_file = DATA_DIR / "tickets.json"

        with open(
            tickets_file,
            "r",
            encoding="utf-8"
        ) as file:

            tickets = json.load(file)

        product_areas = sorted(
            {
                ticket.get("product_area")
                for ticket in tickets
                if ticket.get("product_area")
            }
        )

        return product_areas

    # -----------------------------------------------------
    # Main triage function
    # -----------------------------------------------------

    def triage(
        self,
        subject,
        body
    ):

        if not subject and not body:

            raise ValueError(
                "Ticket subject or body must be provided."
            )

        ticket_text = (
            f"Subject: {subject}\n\n"
            f"Body:\n{body}"
        )

        # -------------------------------------------------
        # Retrieve relevant knowledge-base sections
        # -------------------------------------------------

        retrieved_documents = self.retriever.search(
            ticket_text,
            top_k=4
        )

        knowledge_context = "\n\n".join(
            [
                (
                    f"DOCUMENT: {document['document']}\n"
                    f"HEADING: {document['heading']}\n"
                    f"CONTENT:\n{document['content']}"
                )
                for document in retrieved_documents
            ]
        )

        # -------------------------------------------------
        # Prompt
        # -------------------------------------------------

        prompt = f"""
You are an AI technical support ticket triage agent.

Analyze the incoming support ticket and produce a
structured triage result.

Use ONLY:

1. The incoming support ticket.
2. The supplied product-area values.
3. The supplied issue categories.
4. The supplied urgency values.
5. The retrieved knowledge-base content.

Do not use external data.

ALLOWED PRODUCT AREAS:

{json.dumps(
    self.product_areas,
    indent=2
)}

ALLOWED ISSUE CATEGORIES:

{json.dumps(
    ALLOWED_CATEGORIES,
    indent=2
)}

ALLOWED URGENCY VALUES:

{json.dumps(
    ALLOWED_URGENCY,
    indent=2
)}


INCOMING SUPPORT TICKET

Subject:
{subject}

Body:
{body}


RETRIEVED KNOWLEDGE BASE

{knowledge_context}


TASK REQUIREMENTS

Classify the ticket into:

1. Product area.
2. Issue category.
3. Urgency tier P1-P4.
4. Reasoning for the classification.
5. Whether it matches a known issue.
6. The relevant knowledge-base document.
7. Recommended responder team.
8. Draft first-response message for the support agent.


KNOWN ISSUE RULE

Set known_issue to true only when the incoming ticket
clearly matches a known issue pattern described in the
retrieved knowledge base.

Otherwise set known_issue to false.


FIRST RESPONSE RULE

The draft response must:

- Be professional.
- Acknowledge the customer's issue.
- Be appropriate as a first response.
- Not claim that the issue has already been fixed.
- Not invent information that is not supported by the ticket
  or knowledge base.


CLASSIFICATION RULE

Use the supplied product-area and issue-category values.

Do not invent new product areas or issue categories.
"""

        # -------------------------------------------------
        # Gemini structured output
        # -------------------------------------------------

        print("Generating triage response:")
        print()

        stream = self.client.models.generate_content_stream(
            model=self.model, 
            contents=prompt, 
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=TriageOutput,
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

            result = TriageOutput.model_validate_json(
                response_text
            )

        except Exception as error:

            raise RuntimeError(
                "Could not parse Gemini's streamed "
                "structured response."
        ) from error

        # -------------------------------------------------
        # Validate output
        # -------------------------------------------------

        self._validate_result(result)

        return result

    # -----------------------------------------------------
    # Validate model output
    # -----------------------------------------------------

    def _validate_result(
        self,
        result
    ):

        if result.product_area not in self.product_areas:

            raise ValueError(
                "Invalid product area returned: "
                f"{result.product_area}"
            )

        if result.issue_category not in ALLOWED_CATEGORIES:

            raise ValueError(
                "Invalid issue category returned: "
                f"{result.issue_category}"
            )

        if result.urgency not in ALLOWED_URGENCY:

            raise ValueError(
                "Invalid urgency returned: "
                f"{result.urgency}"
            )


# ---------------------------------------------------------
# Callable Python function required by Task 1
# ---------------------------------------------------------

def triage_ticket(
    subject,
    body
):

    agent = TicketTriageAgent()

    return agent.triage(
        subject=subject,
        body=body
    )


# ---------------------------------------------------------
# Command-line execution
# ---------------------------------------------------------

if __name__ == "__main__":

    print()
    print("===================================")
    print(" Zycus AI Ticket Triage Agent")
    print("===================================")
    print()

    subject = input(
        "Enter ticket subject: "
    ).strip()

    print()

    body = input(
        "Enter ticket body: "
    ).strip()

    print()
    print("Analyzing ticket...")
    print()

    result = triage_ticket(
        subject=subject,
        body=body
    )
