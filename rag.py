
import re
from pathlib import Path


REFUSAL = "Not found in handbook."

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "before",
    "between", "by", "can", "could", "did", "do", "does",
    "for", "from", "get", "gets", "has", "have", "how",
    "i", "in", "into", "is", "it", "its", "may", "me",
    "much", "many", "must", "my", "of", "on", "or",
    "our", "should", "some", "that", "the", "their",
    "there", "these", "this", "those", "time", "to",
    "today", "us", "was", "were", "what", "when",
    "where", "which", "who", "why", "will", "with",
    "would", "you", "your",
}


def normalize(word):
    """Apply simple English word normalization."""
    if len(word) > 5 and word.endswith("ies"):
        return word[:-3] + "y"

    if len(word) > 6 and word.endswith("ing"):
        return word[:-3]

    if len(word) > 5 and word.endswith("ed"):
        return word[:-2]

    if (
        len(word) > 4
        and word.endswith("s")
        and not word.endswith("ss")
    ):
        return word[:-1]

    return word


def get_keywords(text):
    """Extract meaningful, normalized words."""
    words = re.findall(r"[a-z0-9]+", text.lower())

    return [
        normalize(word)
        for word in words
        if word not in STOPWORDS and len(word) > 2
    ]


def load_chunks(path):
    """Read handbook sections into independent chunks."""
    text = Path(path).read_text(encoding="utf-8")

    return [
        part.strip()
        for part in text.split("## ")
        if part.strip()
    ]


def split_chunk(chunk):
    """Separate section title from document body."""
    title, separator, body = chunk.partition("\n")
    return title.strip(), body.strip() if separator else ""


def score_chunk(question_words, chunk):
    """Give title matches more weight than body matches."""
    title, body = split_chunk(chunk)
    terms = set(question_words)

    title_matches = terms & set(get_keywords(title))
    body_matches = terms & set(get_keywords(body))

    return (
        2 * len(title_matches)
        + len(body_matches)
    )


def retrieve(question, chunks):
    """
    Return the most relevant eligible section.

    A section must match at least one title keyword,
    or at least three distinct body keywords.
    """
    question_words = get_keywords(question)

    best_chunk = None
    best_score = 0

    for chunk in chunks:
        title, body = split_chunk(chunk)
        terms = set(question_words)

        title_matches = (
            terms & set(get_keywords(title))
        )

        body_matches = (
            terms & set(get_keywords(body))
        )

        # Reject weak accidental matches.
        if not title_matches and len(body_matches) < 3:
            continue

        score = score_chunk(question_words, chunk)

        if score > best_score:
            best_chunk = chunk
            best_score = score

    return best_chunk, best_score, len(question_words)


def answer(question, chunks):
    """Extract matching evidence and include a section citation."""
    chunk, score, keyword_count = retrieve(
        question, chunks
    )

    if chunk is None:
        return REFUSAL

    title, body = split_chunk(chunk)
    terms = set(get_keywords(question))

    sentences = re.split(
        r"(?<=[.!?])\s+",
        body.replace("\n", " ")
    )

    ranked = []

    for index, sentence in enumerate(sentences):
        matches = len(
            terms & set(get_keywords(sentence))
        )

        if matches > 0:
            ranked.append(
                (matches, index, sentence.strip())
            )

    if not ranked:
        return REFUSAL

    # Prefer strong matches, but retain original text order.
    best_two = sorted(
        ranked,
        key=lambda item: (-item[0], item[1])
    )[:2]

    best_two.sort(key=lambda item: item[1])

    excerpt = " ".join(
        item[2] for item in best_two
    )

    return f"{excerpt} (Source: {title})"


if __name__ == "__main__":
    handbook_path = Path(__file__).with_name(
        "handbook.md"
    )

    chunks = load_chunks(handbook_path)

    print(f"Loaded {len(chunks)} handbook sections.")

    demo_questions = [
        "How much quarterly rebate do distributors receive?",
        "What is required before returning products with an RMA?",
        "What time should employees sleep?",
    ]

    for question in demo_questions:
        print("\nQ:", question)
        print("A:", answer(question, chunks))
