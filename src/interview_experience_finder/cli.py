from __future__ import annotations

import argparse
from typing import Iterable

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .index import IMPORT_CSV, INDEX_DIR, ensure_index, rebuild_index
from .search import search_index

console = Console()


def _result_panel(position: int, result, show_full: bool) -> Panel:
    record = result.record
    body_lines = [
        f"[bold]Question[/bold]\n{record.question}",
    ]
    if record.question_detail:
        body_lines.append(f"[bold]Question detail[/bold]\n{record.question_detail}")
    body_lines.append(f"[bold]Answer[/bold]\n{record.spoken_answer}")
    if record.follow_up_points:
        body_lines.append(f"[bold]Follow-ups[/bold]\n{record.follow_up_points}")
    if show_full:
        body_lines.append(f"[bold]Search text[/bold]\n{record.full_text}")
    body = "\n\n".join(body_lines)
    title = f"#{position}  score={result.score:.3f}"
    subtitle = f"source={record.source_sheet or 'unknown'}  kw={result.keyword_score:.3f}  word={result.word_score:.3f}  char={result.char_score:.3f}"
    return Panel(body, title=title, subtitle=subtitle, expand=False)


def _handle_search(query: str, top_n: int, show_full: bool) -> int:
    index = ensure_index()
    results = search_index(index, query=query, top_n=top_n)
    if not results:
        console.print("[yellow]No matches found.[/yellow]")
        return 1

    display_results = list(reversed(results))

    console.print(f"[bold green]Top matches for:[/bold green] {query} [dim](best shown last)[/dim]\n")
    for idx, result in enumerate(display_results, start=1):
        console.print(_result_panel(idx, result, show_full=show_full))
    return 0


def _handle_reindex() -> int:
    index = rebuild_index()
    console.print(f"[green]Indexed {len(index.records)} stories from[/green] {IMPORT_CSV}")
    console.print(f"[green]Saved index under[/green] {INDEX_DIR}")
    return 0


def _handle_list(limit: int) -> int:
    index = ensure_index()
    table = Table(title="Indexed interview stories")
    table.add_column("#", justify="right")
    table.add_column("Question", overflow="fold")
    table.add_column("Source", overflow="fold")
    for idx, record in enumerate(index.records[:limit], start=1):
        table.add_row(str(idx), record.question, record.source_sheet)
    console.print(table)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="finder", description="Fast local search over behavioral interview experiences")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search for the most relevant experience")
    search_parser.add_argument("query", help="Phrase or keyword to search for")
    search_parser.add_argument("--top", type=int, default=5, help="Number of results to return")
    search_parser.add_argument("--full", action="store_true", help="Show the full indexed text")

    subparsers.add_parser("reindex", help="Rebuild the local search index")

    list_parser = subparsers.add_parser("list", help="List indexed questions")
    list_parser.add_argument("--limit", type=int, default=20, help="How many questions to show")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "search":
        return _handle_search(args.query, top_n=args.top, show_full=args.full)
    if args.command == "reindex":
        return _handle_reindex()
    if args.command == "list":
        return _handle_list(args.limit)

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
