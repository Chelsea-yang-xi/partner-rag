# Partner Policy RAG Assistant


A retrieval-augmented generation (RAG) assistant that answers B2B channel-policy
questions for account managers, grounded in a partner handbook, with built-in
hallucination guardrails and source citation.


> Motivation: as a Key Account Manager at DJI, policy questions from retail
> partners (rebates, trade-in, warranty, MDF) required digging through documents
> daily. This project is the tool I wished I had.


## How It Works
```
Question → [Retrieval: keyword scoring + relevance threshold]
         → [Augment: guardrail prompt assembly]
         → [Generation: pluggable answerer (extractive / LLM API)]
         → Grounded answer + source citation
```


## Key Features
- **Grounded answers**: responses are generated only from retrieved handbook sections
  with the source section cited
- **Hallucination guardrails**: relevance threshold (match-ratio check) rejects
  out-of-scope questions with "Not found in handbook." instead of guessing
- **Pluggable generation**: extractive answerer runs with zero dependencies;
  swap one function to use an LLM API
- **Data/logic separation**: add or edit handbook sections — no code changes needed
- **Tested**: pytest suite includes dedicated hallucination test cases


## Quick Start
```bash
python rag.py          # runs demo questions end-to-end
pytest -v              # runs the test suite incl. hallucination checks
```


## Example
```
Q: How much rebate do I get?
A: Retail partners receive a quarterly volume rebate of 2% when quarterly
   sell-through exceeds EUR 200,000... (Source: Rebate Policy)


Q: What time should I go to sleep?
A: Not found in handbook.        ← guardrail working
```


## Design Notes & Limitations
- Retrieval is keyword-overlap scoring with stop-word filtering; the scoring
  function is isolated so it can be upgraded to embedding-based semantic search
  without touching the rest of the pipeline
- Chunking assumes `## `-delimited markdown sections; PDF ingestion would add
  a parsing layer in front of the same pipeline


## Tech Stack
Python (stdlib only) · pytest
