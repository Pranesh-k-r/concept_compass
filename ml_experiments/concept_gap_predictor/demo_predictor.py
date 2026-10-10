import joblib
import pandas as pd

def demonstrate_prediction():
    print("--- ML Concept Gap Predictor: Standalone Demo ---")
    
    # Check if models exist
    try:
        model = joblib.load('random_forest.pkl')
        feature_columns = joblib.load('feature_columns.pkl')
    except FileNotFoundError:
        print("Model or feature columns not found. Please run train_and_evaluate.py first.")
        return
        
    print("Loaded Random Forest model successfully.")
    
    # Create a mock student profile representation (simulating data from an active session)
    # The student struggled heavily on C02 (Fractions) and C04 (Ratios)
    mock_input = {col: -1.0 for col in feature_columns}  # Start with unattempted (-1)
    
    # Assume student answered C01 (Whole numbers) correctly and fast
    mock_input.update({
        'C01_correct': 1.0,
        'C01_time': 15.0,
        'C01_hints': 0.0
    })
    
    # Assume student answered C02 (Fractions) poorly and slowly
    mock_input.update({
        'C02_correct': 0.0,
        'C02_time': 95.0,
        'C02_hints': 2.0
    })
    
    # Convert to DataFrame
    df_input = pd.DataFrame([mock_input])
    
    # Predict using the model
    prediction = model.predict(df_input)[0]
    
    print("\n[Mock Student Input]")
    print(f"- Mastered C01 (Whole numbers)")
    print(f"- Struggled on C02 (Fractions: 0% correct, 95s time, 2 hints)")
    print("\n[Model Prediction]")
    print(f"Predicted Root Gap Concept ID: {prediction}")
    print("\nNote: Prediction based entirely on experimental ML model without invoking Django dependencies.")

if __name__ == '__main__':
    demonstrate_prediction()
