import pandas as pd

from app.agents.diagnosis_agent import diagnose_payment
from app.agents.recovery_planner import plan_recovery_action
from app.domain.models.payment import PaymentRiskRecord
from app.domain.services import normalize_payment_record
from app.intelligence.classification.rules import classify_failure
# from app.intelligence.features import feature_builder
from app.intelligence.features.feature_builder import build_features
from app.intelligence.models.predict import (
    load_model,
    predict_recovery_probability,
)


def test_day4_end_to_end_integration():
    """
    Day 3 -> Day 4 vertical slice.

    Raw payment
        -> validate
        -> normalize
        -> build Day 3 features
        -> predict recovery probability
        -> classify
        -> diagnose
        -> plan recovery action
    """

    # Load the already-trained Day 3 model.
    model = load_model()

    # Load one real record from the existing dataset.
    dataframe = pd.read_csv(
        "app/data/synthetic/payments.csv"
    )

    raw_payment = dataframe.iloc[0].to_dict()

    # Day 1: validate raw data.
    validated_payment = PaymentRiskRecord(
        **raw_payment
    )

    # Day 1: normalize canonical record.
    payment = normalize_payment_record(
        validated_payment
    )

    # Build the exact Day 3 ML feature set from the same record.
    single_record_df = pd.DataFrame(
        [raw_payment]
    )

    features, _ = build_features(
        single_record_df
    )

    # Day 3: predict recovery probability.
    recovery_probability = predict_recovery_probability(
        model=model,
        features=features,
    )

    # Day 2: deterministic classification.
    failure_category = classify_failure(
        payment.failure_reason
    )

    # Day 4: structured diagnosis.
    diagnosis = diagnose_payment(
        payment=payment,
        failure_category=failure_category,
        recovery_probability=recovery_probability,
    )

    # Day 4: bounded recovery planning.
    recovery_plan = plan_recovery_action(
        payment=payment,
        failure_category=failure_category,
        recovery_probability=recovery_probability,
        diagnosis=diagnosis,
    )

    # Verify the complete vertical slice.
    assert payment.payment_id
    assert failure_category is not None

    assert features.shape[0] == 1
    assert 0.0 <= recovery_probability <= 1.0

    assert diagnosis.summary
    assert diagnosis.reason_codes
    assert 0.0 <= diagnosis.confidence <= 1.0

    assert recovery_plan.action is not None
    assert recovery_plan.expected_recovery_value >= 0.0
    assert recovery_plan.priority_score >= 0.0

    # Verify expected recovery value.
    assert recovery_plan.expected_recovery_value == round(
        payment.amount * recovery_probability,
        2,
    )