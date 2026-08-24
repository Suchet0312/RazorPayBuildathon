from app.domain.enums.failure_category import FailureCategory
from app.domain.models.payment import PaymentRiskRecord
from app.domain.models.recovery import Diagnosis


HIGH_RECOVERY_PROBABILITY_THRESHOLD = 0.70
LOW_RECOVERY_PROBABILITY_THRESHOLD = 0.40

STRONG_CUSTOMER_HISTORY_THRESHOLD = 0.75
WEAK_CUSTOMER_HISTORY_THRESHOLD = 0.40

REPEATED_ATTEMPTS_THRESHOLD = 2


def diagnose_payment(
    payment: PaymentRiskRecord,
    failure_category: FailureCategory,
    recovery_probability: float,
) -> Diagnosis:
    """
    Build a structured and explainable diagnosis for a payment-risk record.

    This function explains the current recovery situation using deterministic
    signals. It does not approve or execute any recovery action.
    """

    reason_codes: list[str] = []
    summary_parts: list[str] = []

    # Failure category signals
    if failure_category == FailureCategory.TEMPORARY_FAILURE:
        reason_codes.append("TEMPORARY_FAILURE")
        summary_parts.append(
            "The payment failed due to a temporary issue, so recovery may still be possible."
        )

    elif failure_category == FailureCategory.CUSTOMER_ACTION_REQUIRED:
        reason_codes.append("CUSTOMER_ACTION_REQUIRED")
        summary_parts.append(
            "The payment requires additional customer action before recovery can occur."
        )

    elif failure_category == FailureCategory.CHECKOUT_ABANDONMENT:
        reason_codes.append("CHECKOUT_ABANDONMENT")
        summary_parts.append(
            "The payment appears to have been abandoned before successful completion."
        )

    elif failure_category == FailureCategory.PERMANENT_FAILURE:
        reason_codes.append("PERMANENT_FAILURE")
        summary_parts.append(
            "The failure appears to be permanent, making automatic recovery unlikely."
        )

    # Recovery probability signals
    if recovery_probability >= HIGH_RECOVERY_PROBABILITY_THRESHOLD:
        reason_codes.append("HIGH_RECOVERY_PROBABILITY")
        summary_parts.append(
            f"The recovery model predicts a strong recovery probability of "
            f"{recovery_probability:.2f}."
        )

    elif recovery_probability <= LOW_RECOVERY_PROBABILITY_THRESHOLD:
        reason_codes.append("LOW_RECOVERY_PROBABILITY")
        summary_parts.append(
            f"The recovery model predicts a low recovery probability of "
            f"{recovery_probability:.2f}."
        )

    else:
        reason_codes.append("MODERATE_RECOVERY_PROBABILITY")
        summary_parts.append(
            f"The recovery model predicts a moderate recovery probability of "
            f"{recovery_probability:.2f}."
        )

    # Attempt history signals
    if payment.attempt_count >= REPEATED_ATTEMPTS_THRESHOLD:
        reason_codes.append("REPEATED_ATTEMPTS")
        summary_parts.append(
            f"The payment has already been attempted {payment.attempt_count} times."
        )

    else:
        reason_codes.append("LOW_ATTEMPT_COUNT")
        summary_parts.append(
            f"The payment has only been attempted {payment.attempt_count} time(s)."
        )

    # Customer history signals
    if payment.customer_success_rate >= STRONG_CUSTOMER_HISTORY_THRESHOLD:
        reason_codes.append("STRONG_CUSTOMER_HISTORY")
        summary_parts.append(
            "The customer has a strong historical payment success rate."
        )

    elif payment.customer_success_rate <= WEAK_CUSTOMER_HISTORY_THRESHOLD:
        reason_codes.append("WEAK_CUSTOMER_HISTORY")
        summary_parts.append(
            "The customer has a weak historical payment success rate."
        )

    # Previous retry history
    if (
        payment.previous_retry_success_rate
        >= STRONG_CUSTOMER_HISTORY_THRESHOLD
    ):
        reason_codes.append("STRONG_RETRY_HISTORY")
        summary_parts.append(
            "Previous retry attempts for similar situations have shown strong success."
        )

    elif (
        payment.previous_retry_success_rate
        <= WEAK_CUSTOMER_HISTORY_THRESHOLD
    ):
        reason_codes.append("WEAK_RETRY_HISTORY")
        summary_parts.append(
            "Previous retry attempts for similar situations have shown weak success."
        )

    # Confidence calculation
    confidence = _calculate_diagnosis_confidence(
        failure_category=failure_category,
        recovery_probability=recovery_probability,
        payment=payment,
    )

    return Diagnosis(
        summary=" ".join(summary_parts),
        reason_codes=reason_codes,
        confidence=confidence,
    )


def _calculate_diagnosis_confidence(
    payment: PaymentRiskRecord,
    failure_category: FailureCategory,
    recovery_probability: float,
) -> float:
    """
    Calculate deterministic confidence for the diagnosis.

    Confidence measures how strongly the available structured signals support
    the diagnosis. It is not a policy approval score.
    """

    confidence = 0.50

    # Known deterministic classification increases confidence.
    if failure_category in {
        FailureCategory.TEMPORARY_FAILURE,
        FailureCategory.CUSTOMER_ACTION_REQUIRED,
        FailureCategory.CHECKOUT_ABANDONMENT,
        FailureCategory.PERMANENT_FAILURE,
    }:
        confidence += 0.15

    # More confident ML predictions increase diagnosis confidence.
    probability_distance = abs(recovery_probability - 0.50)
    confidence += probability_distance * 0.40

    # Historical context contributes additional confidence.
    if (
        payment.customer_success_rate >= STRONG_CUSTOMER_HISTORY_THRESHOLD
        or payment.customer_success_rate <= WEAK_CUSTOMER_HISTORY_THRESHOLD
    ):
        confidence += 0.05

    if (
        payment.previous_retry_success_rate
        >= STRONG_CUSTOMER_HISTORY_THRESHOLD
        or payment.previous_retry_success_rate
        <= WEAK_CUSTOMER_HISTORY_THRESHOLD
    ):
        confidence += 0.05

    return round(min(confidence, 1.0), 4)
