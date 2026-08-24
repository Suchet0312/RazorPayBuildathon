from typing import Optional, Tuple

import pandas as pd

from app.intelligence.classification.rules import classify_failure


FEATURE_COLUMNS = [
    "amount",
    "payment_method",
    "failure_category",
    "attempt_count",
    "customer_success_rate",
    "previous_retry_success_rate",
    "hour_of_day",
    "day_of_week",
]

TARGET_COLUMN = "actual_recovery_outcome"


def build_features(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
    """
    Build reproducible ML features.

    When the recovery outcome target is present, return both features
    and target for training. During inference, return features and None.
    """

    data = df.copy()

    # Parse timestamp
    data["event_timestamp"] = pd.to_datetime(
        data["event_timestamp"],
        errors="raise",
    )

    # Derive deterministic failure category
    data["failure_category"] = data[
        "failure_reason"
    ].apply(
        classify_failure
    )

    # Derive time-based features
    data["hour_of_day"] = (
        data["event_timestamp"].dt.hour
    )

    data["day_of_week"] = (
        data["event_timestamp"].dt.dayofweek
    )

    # Select model features
    X = data[FEATURE_COLUMNS].copy()

    # Training data contains the target.
    # Production inference does not.
    if TARGET_COLUMN in data.columns:
        y = data[TARGET_COLUMN].copy()
    else:
        y = None

    return X, y