import joblib
import pandas as pd
from recommender import generate_improvement_report

def run_demo():
    print("Initializing Improvement Suggestions Demo...")
    
    try:
        model = joblib.load('random_forest.pkl')
        feature_columns = joblib.load('feature_columns.pkl')
    except FileNotFoundError:
        print("Error: Models not found. Please run `python train.py` first.")
        return

    # Create mock student input (unattempted gaps filled with -1.0)
    mock_input = {col: -1.0 for col in feature_columns}
    
    # Simulate a student struggling on Ratios (C04) and Percentages (C05)
    mock_input.update({
        'C04_correct': 0.0,
        'C04_time': 120.0,
        'C04_hints': 3.0,
        'C05_correct': 0.0,
        'C05_time': 90.0,
        'C05_hints': 2.0,
        'C01_correct': 1.0,
        'C01_time': 20.0,
        'C01_hints': 0.0
    })
    
    df_input = pd.DataFrame([mock_input])
    
    # Predict the root concept gap
    try:
        # Some models support predict_proba, Random Forest does
        probabilities = model.predict_proba(df_input)[0]
        max_prob = max(probabilities)
        predicted_gap = model.classes_[probabilities.argmax()]
        
        # Handle uncertainty
        if max_prob < 0.15:
            print("Model is highly uncertain based on the provided inputs.")
            print("Recommendation: More evidence is needed. Please complete a diagnostic quiz first.")
            return
    except AttributeError:
        # Fallback if model doesn't support predict_proba
        predicted_gap = model.predict(df_input)[0]
        
    # Generate the readable report
    report = generate_improvement_report(predicted_gap, mock_input)
    
    print("\n[Output Generated Successfully]")
    print(report)

if __name__ == '__main__':
    run_demo()
