from __future__ import annotations

import csv
import json
import pickle
from pathlib import Path
from typing import List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer

from .models import StoryRecord


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
IMPORTS_DIR = DATA_DIR / "imports"
INDEX_DIR = DATA_DIR / "index"
IMPORT_CSV = IMPORTS_DIR / "behavioral_questions_combined_star.csv"
RECORDS_JSON = INDEX_DIR / "records.json"
INDEX_PKL = INDEX_DIR / "search_index.pkl"


class StoryIndex:
    def __init__(self, records: List[StoryRecord], word_vectorizer, char_vectorizer, word_matrix, char_matrix):
        self.records = records
        self.word_vectorizer = word_vectorizer
        self.char_vectorizer = char_vectorizer
        self.word_matrix = word_matrix
        self.char_matrix = char_matrix


def load_story_records(csv_path: Path = IMPORT_CSV) -> List[StoryRecord]:
    records: List[StoryRecord] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            question = (row.get("Question") or row.get("Questions") or "").strip()
            question_detail = (row.get("Question_Detail") or "").strip()
            source_sheet = (row.get("Source_Sheet") or "").strip()
            pending = (row.get("Pending") or "").strip().lower()
            spoken = (row.get("Answer_STAR") or row.get("Spoken_Answer") or "").strip()
            follow = (row.get("Follow_Up_Points") or "").strip()
            search_text = (row.get("Search_Text") or "").strip()
            if not question:
                continue
            if pending == "yes":
                continue
            if not spoken and not search_text:
                continue
            full_text = search_text or "\n\n".join(part for part in [question, question_detail, spoken, follow] if part).strip()
            records.append(
                StoryRecord(
                    question=question,
                    question_detail=question_detail,
                    source_sheet=source_sheet,
                    spoken_answer=spoken,
                    follow_up_points=follow,
                    full_text=full_text,
                )
            )
    return records


def build_index(records: List[StoryRecord]) -> StoryIndex:
    corpus = [record.full_text for record in records]
    word_vectorizer = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2))
    char_vectorizer = TfidfVectorizer(lowercase=True, analyzer="char_wb", ngram_range=(3, 5))
    word_matrix = word_vectorizer.fit_transform(corpus)
    char_matrix = char_vectorizer.fit_transform(corpus)
    return StoryIndex(records, word_vectorizer, char_vectorizer, word_matrix, char_matrix)


def save_index(index: StoryIndex, index_dir: Path = INDEX_DIR) -> None:
    index_dir.mkdir(parents=True, exist_ok=True)
    RECORDS_JSON.write_text(
        json.dumps([record.to_dict() for record in index.records], indent=2),
        encoding="utf-8",
    )
    payload = {
        "word_vectorizer": index.word_vectorizer,
        "char_vectorizer": index.char_vectorizer,
        "word_matrix": index.word_matrix,
        "char_matrix": index.char_matrix,
    }
    with INDEX_PKL.open("wb") as handle:
        pickle.dump(payload, handle)


def load_index(index_dir: Path = INDEX_DIR) -> Optional[StoryIndex]:
    records_path = index_dir / "records.json"
    index_path = index_dir / "search_index.pkl"
    if not records_path.exists() or not index_path.exists():
        return None
    records = [StoryRecord.from_dict(item) for item in json.loads(records_path.read_text(encoding="utf-8"))]
    with index_path.open("rb") as handle:
        payload = pickle.load(handle)
    return StoryIndex(
        records=records,
        word_vectorizer=payload["word_vectorizer"],
        char_vectorizer=payload["char_vectorizer"],
        word_matrix=payload["word_matrix"],
        char_matrix=payload["char_matrix"],
    )


def rebuild_index(csv_path: Path = IMPORT_CSV, index_dir: Path = INDEX_DIR) -> StoryIndex:
    records = load_story_records(csv_path)
    if not records:
        raise ValueError(f"No searchable records found in {csv_path}")
    index = build_index(records)
    save_index(index, index_dir=index_dir)
    return index


def ensure_index(csv_path: Path = IMPORT_CSV, index_dir: Path = INDEX_DIR) -> StoryIndex:
    current = load_index(index_dir=index_dir)
    if current is not None:
        return current
    return rebuild_index(csv_path=csv_path, index_dir=index_dir)
