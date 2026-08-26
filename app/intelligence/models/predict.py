from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


MODEL_PATH = Path("app/intelligence/artifacts/recovery_model.joblib")


def save_model(
    model: Any,
    model_path: Path = MODEL_PATH,
) -> None:
    """Save the trained recovery model pipeline."""

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)


@lru_cache(maxsize=1)
def load_model(
    model_path: Path = MODEL_PATH,
) -> Any:
    """
    Load the saved recovery model pipeline.

    Result is cached for the lifetime of the process — the model artifact
    is read from disk exactly once, not once per request.
    """

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found: {model_path}"
        )

    return joblib.load(model_path)


def predict_recovery_probability(
    model: Any,
    features: pd.DataFrame,
) -> float:
    """Predict the probability of successful recovery."""

    probability = model.predict_proba(features)[0, 1]
    return float(probability)


def invalidate_model_cache() -> None:
    """
    Clear the in-process model cache.

    Call this after retraining so the next request picks up the new artifact.
    """
    load_model.cache_clear()
