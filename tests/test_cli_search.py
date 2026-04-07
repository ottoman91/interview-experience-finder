from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from interview_experience_finder.index import build_index, load_story_records
from interview_experience_finder.search import search_index


class IngestionTests(unittest.TestCase):
    def test_load_story_records_skips_pending_and_blank_answers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "stories.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["Question", "Question_Detail", "Source_Sheet", "Pending", "Answer_STAR", "Search_Text"],
                )
                writer.writeheader()
                writer.writerow({"Question": "Q1", "Source_Sheet": "Manual", "Pending": "No", "Answer_STAR": "S: one", "Search_Text": "Q1 one"})
                writer.writerow({"Question": "Q2", "Source_Sheet": "Manual", "Pending": "Yes", "Answer_STAR": "S: two", "Search_Text": "Q2 two"})
                writer.writerow({"Question": "Q3", "Source_Sheet": "Manual", "Pending": "No", "Answer_STAR": "", "Search_Text": ""})
            records = load_story_records(path)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].question, "Q1")
        self.assertIn("Q1", records[0].full_text)


class RelevanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        csv_path = Path(__file__).resolve().parents[1] / "data" / "imports" / "behavioral_questions_combined_star.csv"
        cls.index = build_index(load_story_records(csv_path))

    def assert_top_contains(self, query: str, expected_phrase: str) -> None:
        results = search_index(self.index, query, top_n=3)
        self.assertTrue(results, f"No results returned for query: {query}")
        joined = " ".join(result.record.full_text.lower() for result in results)
        self.assertIn(expected_phrase.lower(), joined)

    def test_leadership_without_authority(self) -> None:
        self.assert_top_contains("leadership without authority", "leadership without formal authority")

    def test_overfitting(self) -> None:
        self.assert_top_contains("overfitting", "tax-season unit curves")

    def test_data_engineering(self) -> None:
        self.assert_top_contains("data engineers pipeline instrumentation", "platform health and observability framework")

    def test_ethical_decision(self) -> None:
        self.assert_top_contains("ethical decision", "ethical decision regarding data usage")

    def test_stakeholder_buy_in(self) -> None:
        self.assert_top_contains("stakeholder buy-in", "gain buy-in from skeptical stakeholders")

    def test_data_quality(self) -> None:
        self.assert_top_contains("data quality", "challenging data quality issue")

    def test_conflict_synonym(self) -> None:
        self.assert_top_contains("conflict with teammate", "resolve a conflict within your data science team")


if __name__ == "__main__":
    unittest.main()
