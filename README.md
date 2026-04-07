# Interview Experience Finder

A fast local CLI for pulling up the most relevant behavioral interview experience from your story bank.

## What it does

- indexes your behavioral interview CSV locally
- supports fast phrase lookup like `mistake`, `stakeholder buy-in`, or `leadership without authority`
- returns:
  - question
  - short spoken answer
  - follow-up points
  - match score

## Source data

V1 uses the copied CSV at:

- `data/imports/staff_ds_behavioral_spoken.csv`

To refresh the app after you update your source stories elsewhere:

1. replace `data/imports/staff_ds_behavioral_spoken.csv`
2. run:

```bash
uv run finder reindex
```

## Commands

Search:

```bash
uv run finder search "mistake"
uv run finder search "stakeholder buy-in" --top 3
uv run finder search "technical disagreement" --full
```

Rebuild index:

```bash
uv run finder reindex
```

List all indexed questions:

```bash
uv run finder list --limit 20
```

## Helper script

If you are already in the repo, you can use the local wrapper script instead of typing `uv run` each time:

```bash
./bin/finder search "mistake"
./bin/finder search "leadership without authority" --top 3
./bin/finder reindex
```

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
