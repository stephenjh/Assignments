"""Score headlines with a pretrained sentiment model and write label,headline output."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import joblib
from sentence_transformers import SentenceTransformer


def _usage() -> str:
    return (
        "Usage: python score_headlines.py <input_file> <source>\n"
        "Example: python score_headlines.py todaysheadlines.txt nyt"
    )


def _read_headlines(input_path: Path) -> list[str]:
    lines: list[str] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            headline = line.strip()
            if headline:
                lines.append(headline)
    return lines


def main() -> int:
    """Parse CLI arguments, score headlines, and write the results file."""
    if len(sys.argv) < 3:
        print("Please provide an input file and a source.\n" + _usage())
        return 1

    input_path = Path(sys.argv[1])
    source = sys.argv[2].strip()

    if not source:
        print("Please provide a non-empty source.\n" + _usage())
        return 1

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return 1

    headlines = _read_headlines(input_path)
    if not headlines:
        print(f"No headlines found in {input_path}.")
        return 1

    script_dir = Path(__file__).resolve().parent
    model_path = script_dir / "models" / "svm.joblib"
    if not model_path.exists():
        print(f"Model file not found: {model_path}")
        return 1

    clf = joblib.load(model_path)
    encoder = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = encoder.encode(headlines)
    predictions = clf.predict(embeddings)

    date_str = datetime.now().strftime("%Y_%m_%d")
    output_path = Path(f"headline_scores_{source}_{date_str}.txt")
    with output_path.open("w", encoding="utf-8") as handle:
        for label, headline in zip(predictions, headlines):
            handle.write(f"{label},{headline}\n")

    print(f"Wrote {len(headlines)} scores to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
