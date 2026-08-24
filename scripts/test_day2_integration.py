from app.data.generators.payment_generator import generate_payment_batch
from app.domain.services import (
    normalize_payment_record,
    validate_payment_record,
)
from app.intelligence.classification.rules import classify_failure
from app.workflows.factory import create_recovery_state


def main() -> None:
    generated_records = generate_payment_batch(
        count=5,
        seed=42,
    )

    print("=" * 70)
    print("DAY 2 INTEGRATION TEST")
    print("=" * 70)

    for raw_record in generated_records:
        payment = validate_payment_record(
            raw_record
        )

        normalized_payment = normalize_payment_record(
            payment
        )

        failure_category = classify_failure(
            normalized_payment.failure_reason
        )

        state = create_recovery_state(
            run_id=f"run_{normalized_payment.payment_id}",
            payment=normalized_payment,
        )

        print(
            f"\nPayment ID: {normalized_payment.payment_id}"
        )

        print(
            f"Failure Reason: "
            f"{normalized_payment.failure_reason}"
        )

        print(
            f"Failure Category: "
            f"{failure_category.value}"
        )

        print(
            f"Actual Recovery Outcome: "
            f"{raw_record['actual_recovery_outcome']}"
        )

        print(
            f"Initial State Created: "
            f"{state['run_id']}"
        )

        print("-" * 70)

    print("\nDAY 2 INTEGRATION TEST PASSED")


if __name__ == "__main__":
    main()