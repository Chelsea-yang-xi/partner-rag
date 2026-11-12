
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# The current rag.py loads handbook.md relative to the
# working directory, so run from the project root.
os.chdir(ROOT)

from rag import load_chunks, retrieve, answer


CASES = [
    # Questions with an expected handbook source
    ("P01", "How much quarterly rebate do distributors receive?",
     "Rebate Policy"),
    ("P02", "What information is needed for distributor onboarding?",
     "Distributor Onboarding"),
    ("P03", "When must delivery problems be reported?",
     "Delivery and Logistics"),
    ("P04", "What warranty applies to robotic vacuum products?",
     "Warranty Policy"),
    ("P05", "What is required before returning products with an RMA?",
     "Returns and RMA"),
    ("P06", "What happens to overdue payment balances?",
     "Payment Terms"),
    ("P07", "Where may distributors actively market products?",
     "Geographic Sales Territory"),
    ("P08", "What must an online marketplace listing identify?",
     "Online Marketplace Policy"),
    ("P09", "What information must purchase orders contain?",
     "Purchase Orders"),
    ("P10", "How should distributors use trademarks and brand identifiers?",
     "Brand Protection"),

    # Out-of-scope questions: expected to refuse
    ("N01", "What time should employees sleep?", None),
    ("N02", "What is the weather in London this afternoon?", None),
    ("N03", "Who won the World Cup in 2014?", None),
    ("N04", "How many moons does Jupiter have?", None),
    ("N05", "How do I cook pasta al dente?", None),
    ("N06", "What is the square root of 144?", None),
    ("N07", "Who wrote Hamlet?", None),
    ("N08", "What is the capital of Brazil?", None),
    ("N09", "How do I tune a piano?", None),
    ("N10", "What is the exchange rate between yen and dollar today?", None),
]


def evaluate():
    chunks = load_chunks("handbook.md")
    results = []

    for case_id, question, expected_section in CASES:
        chunk, score, keyword_count = retrieve(
            question, chunks
        )

        actual_section = (
            chunk.splitlines()[0].strip()
            if chunk else None
        )

        response = answer(question, chunks)

        if expected_section is None:
            # Negative: the system should abstain.
            retrieval_correct = None
            citation_correct = None
            passed = (
                response.strip()
                == "Not found in handbook."
            )
        else:
            # Positive: check the retrieved source and
            # whether the answer cites that source.
            retrieval_correct = (
                actual_section == expected_section
            )

            citation_correct = (
                f"(Source: {expected_section})"
                in response
            )

            passed = (
                retrieval_correct
                and citation_correct
            )

        results.append({
            "id": case_id,
            "question": question,
            "expected_section": expected_section,
            "actual_section": actual_section,
            "retrieval_score": score,
            "keyword_count": keyword_count,
            "answer": response,
            "retrieval_correct": retrieval_correct,
            "citation_correct": citation_correct,
            "passed": bool(passed),
        })

    positive = [
        r for r in results
        if r["expected_section"] is not None
    ]

    negative = [
        r for r in results
        if r["expected_section"] is None
    ]

    def rate(numerator, denominator):
        if not denominator:
            return None
        return round(numerator / denominator, 4)

    summary = {
        "total_cases": len(results),
        "passed": sum(r["passed"] for r in results),
        "retrieval_hit_at_1": rate(
            sum(r["retrieval_correct"] for r in positive),
            len(positive),
        ),
        "citation_accuracy_proxy": rate(
            sum(r["citation_correct"] for r in positive),
            len(positive),
        ),
        "refusal_accuracy": rate(
            sum(r["passed"] for r in negative),
            len(negative),
        ),
    }

    report = {
        "evaluated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "system": "keyword-retrieval-baseline",
        "note": (
            "Measures source retrieval, citation presence "
            "and refusal behavior. Does not independently "
            "verify factual answer correctness."
        ),
        "summary": summary,
        "cases": results,
    }

    output = ROOT / "reports" / "baseline_evaluation.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nRAG BASELINE EVALUATION")
    print("=" * 55)

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f'{result["id"]} | {status} | '
            f'{result["question"]}'
        )

    print("\nSUMMARY")
    for key, value in summary.items():
        print(f"{key}: {value}")

    print(f"\nReport saved to: {output}")


if __name__ == "__main__":
    evaluate()
