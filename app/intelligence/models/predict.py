from pathlib import Path
from typing import Any

import joblib


MODEL_PATH = Path("app/intelligence/artifacts/recovery_model.joblib")


def save_model(
    model: Any,
    model_path: Path = MODEL_PATH,
) -> None:
    """
    Save the trained recovery model pipeline.
    """

    model_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        model_path,
    )


def load_model(
    model_path: Path = MODEL_PATH,
) -> Any:
    """
    Load the saved recovery model pipeline.
    """

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found: {model_path}"
        )

    return joblib.load(model_path)

import pandas as pd


def predict_recovery_probability(
    model: Any,
    features: pd.DataFrame,
) -> float:
    """
    Predict the probability of successful recovery.
    """

    probability = model.predict_proba(features)[0, 1]

    return float(probability)