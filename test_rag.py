
from pathlib import Path

import pytest

from rag import answer, load_chunks, retrieve


HANDBOOK = Path(__file__).with_name("handbook.md")
chunks = load_chunks(HANDBOOK)


def test_handbook_loads():
    assert len(chunks) > 0


def test_rebate_question_grounded():
    question = "How much quarterly rebate do distributors receive?"

    chunk, score, total = retrieve(question, chunks)

    assert chunk is not None
    assert chunk.splitlines()[0] == "Rebate Policy"
    assert score > 0


def test_rma_retrieval():
    question = "What is required before returning products with an RMA?"

    chunk, score, total = retrieve(question, chunks)

    assert chunk is not None
    assert chunk.splitlines()[0] == "Returns and RMA"


def test_valid_answer_has_source_citation():
    response = answer(
        "How much quarterly rebate do distributors receive?",
        chunks,
    )

    assert "2%" in response
    assert "(Source: Rebate Policy)" in response


@pytest.mark.parametrize(
    "question",
    [
        "What time should employees sleep?",
        "What time should I go bed?",
        "What is the weather in London this afternoon?",
        "How many moons does Jupiter have?",
        "What is the square root of 144?",
        "What is the capital of Brazil?",
        "What is the exchange rate between yen and dollar today?",
        "How many days of annual leave do I get?",
    ],
)
def test_out_of_scope_questions_are_rejected(question):
    response = answer(question, chunks)

    assert response == "Not found in handbook."


def test_empty_question_is_rejected():
    assert answer("", chunks) == "Not found in handbook."
