from app.data.generators.payment_generator import generate_payment_batch
from app.intelligence.classification.rules import classify_failure


records = generate_payment_batch(
    count=5,
    seed=42,
)


for record in records:
    failure_reason = record["failure_reason"]

    category = classify_failure(
        failure_reason
    )

    print(
        f"Payment: {record['payment_id']}"
    )

    print(
        f"Failure Reason: {failure_reason}"
    )

    print(
        f"Category: {category.value}"
    )

    print(
        f"Recovery Outcome: "
        f"{record['actual_recovery_outcome']}"
    )

    print("-" * 50)