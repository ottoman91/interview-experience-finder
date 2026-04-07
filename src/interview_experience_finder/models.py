from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class StoryRecord:
    question: str
    spoken_answer: str
    follow_up_points: str
    full_text: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "StoryRecord":
        return cls(**data)


@dataclass
class SearchResult:
    record: StoryRecord
    keyword_score: float
    word_score: float
    char_score: float
    score: float
