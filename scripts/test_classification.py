from app.intelligence.classification.rules import (
    classify_failure,
)


failure_reasons = [
    "bank_timeout",
    "network_error",
    "insufficient_funds",
    "inactivity",
    "closed_account",
]


for failure_reason in failure_reasons:
    category = classify_failure(failure_reason)

    print(
        f"{failure_reason} -> {category.value}"
    )