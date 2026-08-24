import pandas as pd

from app.intelligence.features.feature_builder import build_features
from app.intelligence.models.train import split_train_test
from app.intelligence.models.train import (
    split_train_test,
    train_recovery_model,
)
from app.intelligence.models.evaluate import evaluate_model

DATA_PATH = "app/data/synthetic/payments.csv"


def main():
    df = pd.read_csv(DATA_PATH)

    X, y = build_features(df)

    X_train, X_test, y_train, y_test = split_train_test(X, y)

    model = train_recovery_model(X_train, y_train)

    results = evaluate_model(
    model,
    X_test,
    y_test,
)

    print("\n=== HELD-OUT MODEL EVALUATION ===")

    print(f"\nPrecision: {results['precision']:.4f}")
    print(f"Recall: {results['recall']:.4f}")
    print(f"F1 Score: {results['f1_score']:.4f}")
    print(f"ROC-AUC: {results['roc_auc']:.4f}")

    print("\nConfusion Matrix:")
    print(results["confusion_matrix"])

    print("\nClassification Report:")
    print(results["classification_report"])

    # Create a review DataFrame
    inspection_df = X_test.copy()

    inspection_df["actual_outcome"] = y_test.values
    inspection_df["predicted_outcome"] = results["predictions"]
    inspection_df["recovery_probability"] = results["probabilities"]

    # False positives
    false_positives = inspection_df[
        (inspection_df["actual_outcome"] == 0)
        & (inspection_df["predicted_outcome"] == 1)
    ]

    # False negatives
    false_negatives = inspection_df[
        (inspection_df["actual_outcome"] == 1)
        & (inspection_df["predicted_outcome"] == 0)
    ]

    print("\n=== FALSE POSITIVES ===")
    print(false_positives)

    print("\n=== FALSE NEGATIVES ===")
    print(false_negatives)

    print("\nFalse positive count:", len(false_positives))
    print("False negative count:", len(false_negatives))

    print("\n=== MODEL TRAINING TEST ===")

    print("\nModel trained successfully.")

    print("\nTraining score:")
    print(model.score(X_train, y_train))

    print("\nHeld-out test score:")
    print(model.score(X_test, y_test))

    print("\n=== DAY 3 DATA SPLIT TEST ===")

    print("\nTotal records:")
    print(len(X))

    print("\nTraining records:")
    print(len(X_train))

    print("\nHeld-out test records:")
    print(len(X_test))

    print("\nTraining target distribution:")
    print(y_train.value_counts(normalize=True))

    print("\nTest target distribution:")
    print(y_test.value_counts(normalize=True))

    print("\nTrain shape:")
    print(X_train.shape)

    print("\nTest shape:")
    print(X_test.shape)


if __name__ == "__main__":
    main()