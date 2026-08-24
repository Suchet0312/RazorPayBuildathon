from pathlib import Path

import pandas as pd

from app.intelligence.classification.rules import classify_failure


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "app"
    / "data"
    / "synthetic"
    / "payments.csv"
)


def main() -> None:
    dataframe = pd.read_csv(DATA_PATH)

    print("=" * 60)
    print("DATASET OVERVIEW")
    print("=" * 60)

    print(f"\nTotal records: {len(dataframe)}")

    print("\nCOLUMN TYPES:")
    print(dataframe.dtypes)

    print("\nMISSING VALUES:")
    print(dataframe.isnull().sum())

    print("\n" + "=" * 60)
    print("FAILURE REASON DISTRIBUTION")
    print("=" * 60)

    print(
        dataframe["failure_reason"]
        .value_counts()
        .sort_index()
    )

    print("\n" + "=" * 60)
    print("RECOVERY OUTCOME DISTRIBUTION")
    print("=" * 60)

    print(
        dataframe["actual_recovery_outcome"]
        .value_counts()
        .sort_index()
    )

    print("\nRECOVERY RATE:")

    recovery_rate = (
        dataframe["actual_recovery_outcome"]
        .mean()
        * 100
    )

    print(f"{recovery_rate:.2f}%")

    print("\n" + "=" * 60)
    print("FAILURE CATEGORY DISTRIBUTION")
    print("=" * 60)

    dataframe["failure_category"] = (
        dataframe["failure_reason"]
        .apply(
            lambda reason: classify_failure(
                reason
            ).value
        )
    )

    print(
        dataframe["failure_category"]
        .value_counts()
        .sort_index()
    )

    print("\n" + "=" * 60)
    print("RECOVERY RATE BY FAILURE REASON")
    print("=" * 60)

    recovery_by_reason = (
        dataframe
        .groupby("failure_reason")[
            "actual_recovery_outcome"
        ]
        .agg(
            total="count",
            recovered="sum",
            recovery_rate="mean",
        )
    )

    recovery_by_reason[
        "recovery_rate"
    ] = (
        recovery_by_reason[
            "recovery_rate"
        ]
        * 100
    )

    print(
        recovery_by_reason
        .sort_values(
            by="recovery_rate",
            ascending=False,
        )
    )


if __name__ == "__main__":
    main()