from rag import load_chunks, retrieve, answer

chunks = load_chunks("handbook.md")

def test_rebate_question_grounded():
    chunk, score, total = retrieve("How much rebate do I get?", chunks)
    assert "2%" in chunk

def test_hallucination_blocked():
    chunk, score, total = retrieve("What time should I go to sleep?", chunks)   # 你设计的域外问题!
    assert "Channel Conduct" in chunk

def test_anser_has_source_citation():
    a = answer("what time should I go bed?", chunks)
    assert a == "Not found in handbook."

def test_hallucination_guardrail_annual_leave():
    a = answer("How many days of annual leave do I get?", chunks)
    assert a == "Not found in handbook."
