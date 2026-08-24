"""
Module 1 support: RAG engine for the Hyper-Local Business Feasibility Report.

Retrieval: TF-IDF + cosine similarity over chunked knowledge base docs.
  (Swap in sentence-transformers/FAISS or an embeddings API later for
  semantic retrieval — TF-IDF is used here so the whole pipeline runs
  instantly with zero model downloads, good for a hackathon demo.)

Generation: Google Gemini (reuses the same google-genai client pattern
  you were already testing). Falls back to a template-based report if
  no API key is available, so the pipeline still runs end-to-end offline.
"""

import os
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "dummy_docs")


def load_and_chunk_documents(docs_dir: str = DOCS_DIR, chunk_marker: str = "[DOCUMENT:"):
    """
    Splits each .txt file on the [DOCUMENT: ...] marker so each chunk is one
    self-contained knowledge unit (scheme rule, sector note, etc).
    """
    chunks = []
    for filepath in glob.glob(os.path.join(docs_dir, "*.txt")):
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        raw_chunks = content.split(chunk_marker)
        for c in raw_chunks:
            c = c.strip()
            if not c:
                continue
            chunks.append(chunk_marker + c if not c.startswith("DOCUMENT") else c)
    return chunks


class SimpleRetriever:
    def __init__(self, chunks):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(chunks)

    def retrieve(self, query: str, top_k: int = 3):
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        top_indices = scores.argsort()[::-1][:top_k]
        return [(self.chunks[i], float(scores[i])) for i in top_indices if scores[i] > 0]


def build_retriever() -> SimpleRetriever:
    chunks = load_and_chunk_documents()
    return SimpleRetriever(chunks)


def generate_with_gemini(prompt: str) -> str:
    """Calls Gemini if GEMINI_API_KEY is set; raises if not configured."""
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)
    chat = client.chats.create(model="gemini-3.6-flash")
    response = chat.send_message(prompt)
    return response.text


def generate_feasibility_report(village_stats: dict, competitor_density: dict,
                                 sector: str, retrieved_chunks: list) -> str:
    """
    Builds the prompt from retrieved context + structured local stats,
    then generates via Gemini. Falls back to a plain template if no
    API key is configured, so this still works for an offline demo.
    """
    context_text = "\n\n".join(chunk for chunk, score in retrieved_chunks)

    prompt = f"""You are a business advisory assistant for rural micro-entrepreneurs in India.
Using ONLY the context below and the structured local data, produce a Hyper-Local
Business Feasibility Report for a {sector} enterprise.

Structured local data:
{village_stats}

Competitor density: {competitor_density}

Retrieved knowledge base context:
{context_text}

Write the report with these exact sections:
1. Market Reach
2. Opportunity Analysis
3. SWOT
4. Threats
5. Competitor Mapping
6. Product Market Value & Pricing

Keep it concise, practical, and specific to the numbers given. Do not invent
statistics beyond what's provided."""

    try:
        return generate_with_gemini(prompt)
    except Exception as e:
        return _fallback_template_report(village_stats, competitor_density, sector, context_text, reason=str(e))


def _fallback_template_report(village_stats, competitor_density, sector, context_text, reason=""):
    return f"""[FALLBACK TEMPLATE REPORT — LLM generation unavailable: {reason}]

=== Hyper-Local Business Feasibility Report ({sector.title()}) ===

Village: {village_stats.get('village')}, Block: {village_stats.get('block')}
Population: {village_stats.get('population')} | Households: {village_stats.get('households')}
Avg monthly household income: Rs.{village_stats.get('avg_monthly_income_inr')}

1. Market Reach: Immediate consumer base is the village's {village_stats.get('households')} households,
   with secondary reach toward the nearest town ({village_stats.get('nearest_town_distance_km')} km away).

2. Competitor Mapping: {competitor_density}

3. Retrieved sector knowledge used for analysis:
{context_text}

(Set GEMINI_API_KEY to generate a full narrative SWOT/opportunity/pricing report instead of this template.)
"""


if __name__ == "__main__":
    retriever = build_retriever()
    results = retriever.retrieve("dairy sector opportunities and threats", top_k=3)
    for chunk, score in results:
        print(f"[{score:.3f}] {chunk[:80]}...")
