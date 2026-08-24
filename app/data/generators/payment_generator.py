from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any


RANDOM_SEED = 42


FAILURE_REASONS = {
    "bank_timeout": "TEMPORARY_FAILURE",
    "network_error": "TEMPORARY_FAILURE",
    "processing_error": "TEMPORARY_FAILURE",

    "authentication_failed": "CUSTOMER_ACTION_REQUIRED",
    "insufficient_funds": "CUSTOMER_ACTION_REQUIRED",
    "payment_method_declined": "CUSTOMER_ACTION_REQUIRED",

    "inactivity": "CHECKOUT_ABANDONMENT",
    "repeated_attempts": "CHECKOUT_ABANDONMENT",
    "payment_method_switch": "CHECKOUT_ABANDONMENT",

    "invalid_details": "PERMANENT_FAILURE",
    "closed_account": "PERMANENT_FAILURE",
    "blocked_payment": "PERMANENT_FAILURE",
}


PAYMENT_METHODS = [
    "upi",
    "card",
    "netbanking",
    "wallet",
]


FAILURE_WEIGHTS = {
    "bank_timeout": 12,
    "network_error": 10,
    "processing_error": 8,

    "authentication_failed": 8,
    "insufficient_funds": 10,
    "payment_method_declined": 8,

    "inactivity": 8,
    "repeated_attempts": 6,
    "payment_method_switch": 5,

    "invalid_details": 6,
    "closed_account": 4,
    "blocked_payment": 5,
}


def generate_failure_reason(rng: random.Random) -> str:
    """
    Generate a realistic payment failure reason using
    weighted random selection.
    """

    reasons = list(FAILURE_WEIGHTS.keys())
    weights = list(FAILURE_WEIGHTS.values())

    return rng.choices(
        population=reasons,
        weights=weights,
        k=1,
    )[0]


def calculate_recovery_probability(
    failure_reason: str,
    customer_success_rate: float,
    previous_retry_success_rate: float,
    attempt_count: int,
) -> float:
    """
    Generate the hidden probability used to create the
    synthetic ground-truth recovery label.
    """

    base_probabilities = {
        "bank_timeout": 0.80,
        "network_error": 0.75,
        "processing_error": 0.65,

        "authentication_failed": 0.55,
        "insufficient_funds": 0.45,
        "payment_method_declined": 0.40,

        "inactivity": 0.50,
        "repeated_attempts": 0.35,
        "payment_method_switch": 0.45,

        "invalid_details": 0.10,
        "closed_account": 0.02,
        "blocked_payment": 0.05,
    }

    probability = base_probabilities[failure_reason]

    customer_adjustment = (
        customer_success_rate - 0.5
    ) * 0.30

    retry_adjustment = (
        previous_retry_success_rate - 0.5
    ) * 0.25

    attempt_penalty = max(
        0,
        attempt_count - 1,
    ) * 0.08

    probability += customer_adjustment
    probability += retry_adjustment
    probability -= attempt_penalty

    return round(
        max(0.01, min(probability, 0.99)),
        4,
    )


def assign_recovery_label(
    rng: random.Random,
    failure_reason: str,
    customer_success_rate: float,
    previous_retry_success_rate: float,
    attempt_count: int,
) -> int:
    """
    Assign the synthetic ground-truth recovery outcome.

    1 = recovered
    0 = not recovered
    """

    probability = calculate_recovery_probability(
        failure_reason=failure_reason,
        customer_success_rate=customer_success_rate,
        previous_retry_success_rate=previous_retry_success_rate,
        attempt_count=attempt_count,
    )

    return int(
        rng.random() < probability
    )


def generate_payment_record(
    index: int,
    rng: random.Random,
) -> dict[str, Any]:
    """
    Generate one synthetic payment-risk record.
    """

    failure_reason = generate_failure_reason(rng)

    customer_success_rate = round(
        rng.uniform(0.20, 0.99),
        2,
    )

    previous_retry_success_rate = round(
        rng.uniform(0.10, 0.95),
        2,
    )

    attempt_count = rng.randint(1, 5)

    contact_count = rng.randint(0, 2)

    event_timestamp = (
        datetime(2026, 1, 1)
        + timedelta(
            minutes=rng.randint(
                0,
                60 * 24 * 180,
            )
        )
    )

    actual_recovery_outcome = assign_recovery_label(
        rng=rng,
        failure_reason=failure_reason,
        customer_success_rate=customer_success_rate,
        previous_retry_success_rate=previous_retry_success_rate,
        attempt_count=attempt_count,
    )

    return {
        "payment_id": f"pay_{index:06d}",
        "customer_id": f"cust_{rng.randint(1, 300):04d}",
        "merchant_id": f"merchant_{rng.randint(1, 20):03d}",
        "amount": round(
            rng.uniform(100, 20000),
            2,
        ),
        "currency": "INR",
        "payment_method": rng.choice(
            PAYMENT_METHODS
        ),
        "status": "failed",
        "failure_reason": failure_reason,
        "attempt_count": attempt_count,
        "event_timestamp": event_timestamp.isoformat(),
        "customer_success_rate": customer_success_rate,
        "previous_retry_success_rate": previous_retry_success_rate,
        "contact_count": contact_count,
        "actual_recovery_outcome": actual_recovery_outcome,
    }


def generate_payment_batch(
    count: int,
    seed: int = RANDOM_SEED,
    start_index: int = 1,
) -> list[dict[str, Any]]:
    """
    Generate a reproducible batch of payment-risk records.
    """

    rng = random.Random(seed)

    return [
        generate_payment_record(
            index=start_index + offset,
            rng=rng,
        )
        for offset in range(count)
    ]