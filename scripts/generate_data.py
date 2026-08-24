from pathlib import Path

import pandas as pd

from app.data.generators.payment_generator import generate_payment_batch


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SYNTHETIC_DATA_DIR = (
    PROJECT_ROOT / "app" / "data" / "synthetic"
)

SYNTHETIC_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


DEVELOPMENT_RECORD_COUNT = 500
DEMO_RECORD_COUNT = 100


def main() -> None:
    development_records = generate_payment_batch(
        count=DEVELOPMENT_RECORD_COUNT,
        seed=42,
        start_index=1,
    )

    demo_records = generate_payment_batch(
        count=DEMO_RECORD_COUNT,
        seed=99,
        start_index=100001,
    )

    development_dataframe = pd.DataFrame(
        development_records
    )

    demo_dataframe = pd.DataFrame(
        demo_records
    )

    development_path = (
        SYNTHETIC_DATA_DIR / "payments.csv"
    )

    demo_path = (
        SYNTHETIC_DATA_DIR / "demo_batch.csv"
    )

    development_dataframe.to_csv(
        development_path,
        index=False,
    )

    demo_dataframe.to_csv(
        demo_path,
        index=False,
    )

    print("DATA GENERATION COMPLETE\n")

    print(
        f"Development records: "
        f"{len(development_dataframe)}"
    )

    print(
        f"Demo records: "
        f"{len(demo_dataframe)}"
    )

    print(f"\nSaved: {development_path}")
    print(f"Saved: {demo_path}")

    print("\nDEVELOPMENT DATA PREVIEW:")
    print(
        development_dataframe.head()
    )

    print("\nDEMO DATA PREVIEW:")
    print(
        demo_dataframe.head()
    )


if __name__ == "__main__":
    main()