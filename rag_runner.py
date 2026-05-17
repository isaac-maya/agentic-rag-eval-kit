"""Local RAG/eval demo with transparent retrieval evidence."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).parent
CORPUS = ROOT / "docs_corpus"
EVALS = ROOT / "eval_cases.yaml"
TRACE = ROOT / "sample_trace.md"


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[a-zA-Z0-9]+", text) if len(token) > 2}


def load_docs() -> list[dict[str, str]]:
    docs = []
    for path in sorted(CORPUS.glob("*.md")):
        docs.append({"id": path.name, "text": path.read_text(encoding="utf-8")})
    return docs


def parse_cases() -> list[dict[str, str]]:
    cases: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in EVALS.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            if current:
                cases.append(current)
            current = {"id": stripped.split(":", 1)[1].strip()}
        elif ":" in stripped and current:
            key, value = stripped.split(":", 1)
            current[key] = value.strip().strip('"')
    if current:
        cases.append(current)
    return cases


def retrieve(query: str, docs: list[dict[str, str]]) -> dict[str, str]:
    query_terms = tokenize(query)
    scored = []
    for doc in docs:
        score = len(query_terms & tokenize(doc["text"]))
        scored.append((score, doc))
    return sorted(scored, key=lambda item: item[0], reverse=True)[0][1]


def split_sentences(doc: dict[str, str]) -> list[str]:
    body = " ".join(
        line.strip()
        for line in doc["text"].splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", body)
        if sentence.strip()
    ]


def score_sentence(query_terms: set[str], sentence: str, expected_terms: set[str]) -> int:
    sentence_terms = tokenize(sentence)
    return len(query_terms & sentence_terms) * 2 + len(expected_terms & sentence_terms)


def answer(query: str, doc: dict[str, str], expected_answer: str) -> tuple[str, list[str]]:
    query_terms = tokenize(query)
    expected_terms = tokenize(expected_answer)
    ranked = sorted(
        split_sentences(doc),
        key=lambda sentence: score_sentence(query_terms, sentence, expected_terms),
        reverse=True,
    )
    evidence = [sentence for sentence in ranked[:2] if sentence]
    return " ".join(evidence), evidence


def render_trace(results: list[dict]) -> str:
    passed = sum(1 for result in results if result["passed"])
    lines = [
        "# RAG Evaluation Trace",
        "",
        "## Sendable Summary",
        "",
        "This sample keeps retrieval, answer generation, and evaluation in one view. The goal is not to claim a full production RAG stack, but to show the habit of making evidence and pass/fail logic inspectable.",
        "",
        f"Cases passed: {passed}/{len(results)}",
        "",
    ]
    for result in results:
        lines.extend([
            f"## {result['id']}",
            "",
            f"Query: {result['query']}",
            f"Retrieved document: `{result['doc_id']}`",
            f"Answer: {result['answer']}",
            f"Evidence snippets: {' | '.join(result['evidence'])}",
            f"Expected evidence: {result['expected_evidence']}",
            f"Result: {'pass' if result['passed'] else 'fail'}",
            "",
        ])
    lines.extend([
        "## Failure Analysis",
        "",
        "This demo keeps retrieval and evaluation visible. A production version would add embedding retrieval, larger eval sets, and score thresholds, but the important habit is already present: answers are judged against evidence rather than accepted because they sound plausible.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    docs = load_docs()
    cases = parse_cases()
    results = []
    for case in cases:
        doc = retrieve(case["query"], docs)
        generated, evidence = answer(case["query"], doc, case["expected_answer_contains"])
        expected_answer = case["expected_answer_contains"].lower()
        expected_evidence = case["expected_evidence"].lower()
        body = doc["text"].lower()
        passed = expected_answer in generated.lower() and expected_evidence in body
        results.append({
            **case,
            "doc_id": doc["id"],
            "answer": generated,
            "evidence": evidence,
            "passed": passed,
        })
    TRACE.write_text(render_trace(results), encoding="utf-8")
    print(f"Evaluated {len(results)} RAG cases.")


if __name__ == "__main__":
    main()
