from __future__ import annotations

import re
from typing import List

from sklearn.metrics.pairwise import linear_kernel

from .index import StoryIndex
from .models import SearchResult

TOKEN_RE = re.compile(r"[a-z0-9]+")


def normalize(text: str) -> str:
    return " ".join(TOKEN_RE.findall((text or "").lower()))


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall((text or "").lower())


def keyword_score(query: str, question: str, full_text: str) -> float:
    normalized_query = normalize(query)
    query_tokens = set(tokenize(query))
    if not normalized_query or not query_tokens:
        return 0.0

    question_norm = normalize(question)
    full_norm = normalize(full_text)
    question_tokens = set(question_norm.split())
    full_tokens = set(full_norm.split())

    overlap_full = len(query_tokens & full_tokens) / len(query_tokens)
    overlap_question = len(query_tokens & question_tokens) / len(query_tokens)

    score = 0.45 * overlap_full + 0.35 * overlap_question
    if normalized_query in question_norm:
        score += 0.35
    elif normalized_query in full_norm:
        score += 0.2

    query_words = normalized_query.split()
    if len(query_words) > 1:
        matched_bigrams = 0
        for left, right in zip(query_words, query_words[1:]):
            phrase = f"{left} {right}"
            if phrase in question_norm:
                matched_bigrams += 1
                score += 0.12
            elif phrase in full_norm:
                matched_bigrams += 1
                score += 0.06
        if matched_bigrams:
            score += 0.05 * matched_bigrams / max(len(query_words) - 1, 1)

    return min(score, 1.5)


def search_index(index: StoryIndex, query: str, top_n: int = 5) -> List[SearchResult]:
    normalized_query = normalize(query)
    if not normalized_query:
        return []

    word_query = index.word_vectorizer.transform([query])
    char_query = index.char_vectorizer.transform([query])
    word_scores = linear_kernel(word_query, index.word_matrix).ravel()
    char_scores = linear_kernel(char_query, index.char_matrix).ravel()

    results: List[SearchResult] = []
    for idx, record in enumerate(index.records):
        kw_score = keyword_score(query, record.question, record.full_text)
        word_score = float(word_scores[idx])
        char_score = float(char_scores[idx])
        total = (0.45 * kw_score) + (0.35 * word_score) + (0.20 * char_score)
        results.append(
            SearchResult(
                record=record,
                keyword_score=kw_score,
                word_score=word_score,
                char_score=char_score,
                score=total,
            )
        )

    results.sort(key=lambda item: item.score, reverse=True)
    return results[:top_n]
