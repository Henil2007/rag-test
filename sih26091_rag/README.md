# SIH26091 — Hyper-Local Business Advisory & Financial Structuring Assistant

Working prototype with **dummy data** for the RAG + financial calculator pipeline.

## Architecture

```
Input: village, margin capital, business sector
        │
        ├─► Module 2: financial_calculator.py   (deterministic, no LLM)
        │     margin capital → project cost → scheme routing → EMI schedule
        │
        └─► Module 1: rag_engine.py + local_data.py   (RAG)
              ├── local_data.py    → structured lookup (village CSV: population,
              │                       households, existing competitor counts)
              ├── rag_engine.py    → TF-IDF retrieval over chunked knowledge base
              │                       (data/dummy_docs/*.txt) + Gemini generation
              └── main.py          → combines both into one report
```

### Why the financial calculator is NOT part of the RAG/LLM flow
Loan amounts, interest rates, and EMI figures must be exact. LLMs are unreliable
at arithmetic and could hallucinate scheme numbers, which is dangerous for a
tool guiding real borrowing decisions. `financial_calculator.py` is plain
Python using the exact rules from the PS document (hardcoded scheme config at
the top of the file — swap this for a database/admin panel later if scheme
terms need to change without a code deploy).

### Why structured local stats are separate from the text retriever
Village-level numbers (population, existing competitor counts) are queried
directly from `local_data.py` / the CSV — not embedded as prose and
semantically searched. Mixing structured numeric lookups into a text
retriever is a common RAG mistake; it makes numbers unreliable. The RAG
retriever (`rag_engine.py`) is reserved for genuinely unstructured knowledge:
scheme rules explained in prose, sector business notes, SWOT framework text.

## Files

| File | Purpose |
|---|---|
| `data/dummy_docs/scheme_rules.txt` | Knowledge base: scheme rules in prose, sector notes (dairy/retail/textile), SWOT framework. Chunked on `[DOCUMENT: ...]` markers. |
| `data/dummy_local_stats.csv` | Dummy village-level stats — population, households, existing unit counts per sector, distance to nearest town. **Replace with real Census/MSME/Agri-census data for production.** |
| `src/financial_calculator.py` | Module 2 — deterministic scheme routing, project cost, loan amount, EMI. |
| `src/local_data.py` | Structured village stats lookup + competitor density calculation. |
| `src/rag_engine.py` | Chunking, TF-IDF retriever, Gemini generation (with offline fallback template). |
| `src/main.py` | Orchestrates everything end to end. |

## Running it

```bash
pip install -r requirements.txt
cd src
python3 main.py
```

To get real LLM-generated narrative reports (not the fallback template), set
your Gemini key first:

```bash
export GEMINI_API_KEY="your-key-here"     # macOS/Linux
setx GEMINI_API_KEY "your-key-here"       # Windows (new terminal after)
```

Edit the `run(...)` call at the bottom of `main.py` to test different inputs:
```python
run(village_name="Bavla Chowk", margin_capital=250_000, sector="retail")
```

## Current limitations (dummy-data stage) — known next steps

1. **Retrieval is TF-IDF, not semantic embeddings.** It works for this small
   demo KB but will retrieve loosely-related sector docs alongside the
   correct one (you'll see this in the test run — dairy queries also pull in
   retail/textile notes because of shared generic words like
   "opportunity"/"threats"). For the real hackathon build, swap in
   `sentence-transformers` + FAISS/Chroma for genuine semantic retrieval —
   the `SimpleRetriever` class in `rag_engine.py` is written so this is a
   drop-in replacement (same `.retrieve(query, top_k)` interface).

2. **Local stats are 8 dummy villages.** Real hyper-local grounding needs a
   real data source — Census 2011 village-level data (population/households),
   MSME registration data (Udyam) for competitor density, or state
   agriculture/economic survey data for purchasing power estimates. Plan
   which of these you can realistically pull/scrape before the demo.

3. **Gemini model name**: this uses `gemini-2.5-flash`. Verify against
   whichever model string is current for your API tier before the demo —
   model names change.

4. **No multilingual layer yet.** The PS explicitly asks for a multilingual
   assistant. Easiest path: keep the KB and calculator in English, and add a
   translation pass (input translated to English before retrieval, output
   translated back) rather than maintaining multilingual embeddings.
