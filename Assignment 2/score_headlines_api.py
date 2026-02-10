"""FastAPI service to score headline sentiment."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, List, Protocol, Sequence

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

app = FastAPI(title="Headline Sentiment API")


class HeadlinesRequest(BaseModel):
    """Request payload containing headlines to score."""

    headlines: List[str] = Field(..., description="List of headlines to score")


class Predictor(Protocol):
    """Protocol for classifier-like predictors."""

    def predict(self, features: Any) -> Sequence[str] | Sequence[int]:
        """Return predictions for the provided feature matrix."""
        raise NotImplementedError


def _load_model() -> tuple[Predictor, SentenceTransformer]:
    script_dir = Path(__file__).resolve().parent
    model_path = script_dir / "models" / "svm.joblib"
    if not model_path.exists():
        logger.critical("Model file not found: %s", model_path)
        raise FileNotFoundError(f"Model file not found: {model_path}")

    clf = joblib.load(model_path)
    encoder = SentenceTransformer("all-MiniLM-L6-v2")
    return clf, encoder


try:
    CLASSIFIER, ENCODER = _load_model()
    logger.info("Loaded sentiment model and encoder")
except Exception:
    logger.exception("Failed to load model artifacts")
    raise


@app.get("/status")
def status() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "OK"}


@app.post("/score_headlines")
def score_headlines(payload: HeadlinesRequest) -> dict[str, list[str | int]]:
    """Score headlines and return labels."""
    if not payload.headlines:
        logger.warning("Received empty headlines list")
        raise HTTPException(status_code=400, detail="headlines must be non-empty")

    cleaned = [headline.strip() for headline in payload.headlines if headline.strip()]
    if not cleaned:
        logger.warning("Received headlines list with only empty strings")
        raise HTTPException(status_code=400, detail="headlines must contain text")

    logger.info("Scoring %d headlines", len(cleaned))
    try:
        embeddings = ENCODER.encode(cleaned)
        predictions = CLASSIFIER.predict(embeddings)
    except Exception as exc:
        logger.error("Failed to score headlines: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to score headlines"
        ) from exc

    return {"labels": list(predictions)}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8081"))
    uvicorn.run("score_headlines_api:app", host="0.0.0.0", port=port, reload=False)
