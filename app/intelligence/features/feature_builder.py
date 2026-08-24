from typing import Tuple

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


def build_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Build reproducible ML features and target from payment records.
    """

    data = df.copy()

    # Parse timestamp
    data["event_timestamp"] = pd.to_datetime(
        data["event_timestamp"],
        errors="raise",
    )

    # Derive deterministic failure category
    data["failure_category"] = data["failure_reason"].apply(
        classify_failure
    )

    # Derive time-based features
    data["hour_of_day"] = data["event_timestamp"].dt.hour
    data["day_of_week"] = data["event_timestamp"].dt.dayofweek

    # Select model features
    X = data[FEATURE_COLUMNS].copy()

    # Preserve recovery outcome as target
    y = data[TARGET_COLUMN].copy()

    return X, y