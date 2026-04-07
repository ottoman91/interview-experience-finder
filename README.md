# Interview Experience Finder

A fast local CLI for pulling up the most relevant behavioral interview experience from your story bank.

## What it does

- indexes your behavioral interview CSV locally
- supports fast phrase lookup like `mistake`, `stakeholder buy-in`, or `leadership without authority`
- returns:
  - question
  - question detail when available
  - STAR-formatted answer
  - source sheet
  - match score

## Quick Start

From anywhere on your machine, you can now use:

```bash
ifind "mistake"
ifind "stakeholder buy-in"
ifind "leadership without authority"
```

The global `ifind` command automatically treats plain text as a search query.
You can also still use explicit commands when needed:

```bash
ifind search "technical disagreement"
ifind reindex
ifind list --limit 20
```

If you are already inside the repo, these also work:

```bash
./bin/ifind "mistake"
./bin/finder search "mistake"
```

## Source data

V1 now uses the richer combined CSV at:

- `data/imports/behavioral_questions_combined_star.csv`

That file includes:
- the combined deduplicated question list
- sheet-priority preservation
- STAR-formatted answers
- Amazon principle detail text
- a prebuilt `Search_Text` field for richer retrieval

To refresh the app after you update your source stories elsewhere:

1. replace `data/imports/behavioral_questions_combined_star.csv`
2. run:

```bash
ifind reindex
```

## Commands

Search:

```bash
ifind "mistake"
ifind search "stakeholder buy-in" --top 3
ifind search "technical disagreement" --full
```

Rebuild index:

```bash
ifind reindex
```

List all indexed questions:

```bash
ifind list --limit 20
```

## Output behavior

- search still ranks the strongest matches first internally
- but results are printed weakest-to-strongest within the top set
- that means the best match appears last at the bottom of the terminal output

## How ranking works

This app uses a local hybrid search strategy:

- keyword overlap and phrase matching
- TF-IDF cosine similarity on full story text
- character n-gram TF-IDF for fuzzier phrasing

No external APIs or network calls are used.

## Development

Run tests:

```bash
uv run python -m unittest discover -s tests -v
```
