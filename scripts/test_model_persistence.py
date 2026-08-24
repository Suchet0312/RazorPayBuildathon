import pandas as pd

from app.intelligence.features.feature_builder import build_features
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
    print("\n=== MODEL PERSISTENCE TEST ===")

    # Load development data
    df = pd.read_csv(DATA_PATH)

    # Build features
    X, y = build_features(df)

    # Create frozen split
    X_train, X_test, y_train, y_test = split_train_test(X, y)

    # Train
    model = train_recovery_model(
        X_train,
        y_train,
    )

    print("\nModel trained successfully.")

    # Save
    save_model(model)

    print("Model saved successfully.")

    # Reload
    loaded_model = load_model()

    print("Model reloaded successfully.")

    # Take one held-out sample
    sample_features = X_test.iloc[[0]]

    # Predict probability
    probability = predict_recovery_probability(
        loaded_model,
        sample_features,
    )

    print("\n=== SAMPLE PREDICTION ===")

    print("\nSample features:")
    print(sample_features)

    print(f"\nRecovery probability: {probability:.4f}")

    print(
        f"Actual recovery outcome: "
        f"{y_test.iloc[0]}"
    )


if __name__ == "__main__":
    main()