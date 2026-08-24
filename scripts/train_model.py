import pandas as pd

from app.intelligence.features.feature_builder import build_features
from app.intelligence.models.evaluate import evaluate_model
from app.intelligence.models.predict import (
    load_model,
    predict_recovery_probability,
    save_model,
)
from app.intelligence.models.train import (
    split_train_test,
    train_recovery_model,
)


DATA_PATH = "app/data/synthetic/payments.csv"


def main():
    print("\n=== RAZORPAY RECOVERY BRAIN: DAY 3 MODEL TRAINING ===")

    # 1. Load development data
    df = pd.read_csv(DATA_PATH)
    print(f"\nLoaded records: {len(df)}")

    # 2. Build features
    X, y = build_features(df)
    print(f"Feature matrix shape: {X.shape}")

    # 3. Frozen 80/20 split
    X_train, X_test, y_train, y_test = split_train_test(X, y)

    print(f"\nTraining records: {len(X_train)}")
    print(f"Held-out test records: {len(X_test)}")

    # 4. Train model
    model = train_recovery_model(X_train, y_train)
    print("\nModel training completed.")

    # 5. Evaluate on held-out data
    results = evaluate_model(
        model,
        X_test,
        y_test,
    )

    print("\n=== HELD-OUT EVALUATION ===")
    print(f"Precision: {results['precision']:.4f}")
    print(f"Recall:    {results['recall']:.4f}")
    print(f"F1 Score:  {results['f1_score']:.4f}")
    print(f"ROC-AUC:   {results['roc_auc']:.4f}")

    print("\nConfusion Matrix:")
    print(results["confusion_matrix"])

    # 6. Inspect incorrect predictions
    inspection_df = X_test.copy()
    inspection_df["actual_outcome"] = y_test.values
    inspection_df["predicted_outcome"] = results["predictions"]
    inspection_df["recovery_probability"] = results["probabilities"]

    false_positives = inspection_df[
        (inspection_df["actual_outcome"] == 0)
        & (inspection_df["predicted_outcome"] == 1)
    ]

    false_negatives = inspection_df[
        (inspection_df["actual_outcome"] == 1)
        & (inspection_df["predicted_outcome"] == 0)
    ]

    print("\n=== ERROR ANALYSIS ===")
    print(f"False positives: {len(false_positives)}")
    print(f"False negatives: {len(false_negatives)}")

    # 7. Save model
    save_model(model)
    print("\nModel artifact saved successfully.")

    # 8. Reload model
    loaded_model = load_model()
    print("Model artifact reloaded successfully.")

    # 9. Predict one held-out sample
    sample_features = X_test.iloc[[0]]

    probability = predict_recovery_probability(
        loaded_model,
        sample_features,
    )

    print("\n=== SAMPLE PREDICTION AFTER RELOAD ===")
    print(f"Recovery probability: {probability:.4f}")
    print(f"Actual outcome: {y_test.iloc[0]}")

    print("\n=== DAY 3 TRAINING PIPELINE COMPLETE ===")


if __name__ == "__main__":
    main()