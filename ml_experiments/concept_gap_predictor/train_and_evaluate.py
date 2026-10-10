import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def main():
    print("Loading datasets...")
    # Read-only inspection
    profiles_df = pd.read_csv('../../Datasets/annotated_profiles.csv')
    responses_df = pd.read_csv('../../Datasets/student_responses.csv')
    
    print("Engineering features...")
    # Pivot responses to get correctness per concept per profile
    concept_acc = responses_df.groupby(['profile_id', 'concept_id'])['is_correct'].mean().unstack()
    concept_acc.columns = [f"{c}_correct" for c in concept_acc.columns]
    
    time_spent = responses_df.groupby(['profile_id', 'concept_id'])['time_seconds'].mean().unstack()
    time_spent.columns = [f"{c}_time" for c in time_spent.columns]
    
    hints = responses_df.groupby(['profile_id', 'concept_id'])['hints_used'].mean().unstack()
    hints.columns = [f"{c}_hints" for c in hints.columns]
    
    data = profiles_df[['profile_id', 'annotated_root_gap_concept_id']].set_index('profile_id')
    
    # Combine features. Missing values mean unattempted, filled with -1
    X = pd.concat([concept_acc, time_spent, hints], axis=1).fillna(-1)
    y = data.loc[X.index, 'annotated_root_gap_concept_id']
    
    # Leakage-safe split: Since each row is a unique profile, a standard stratify split prevents leakage between profiles
    # 70% Train, 15% Val, 15% Test
    X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.1765, random_state=42, stratify=y_train_val)
    
    print(f"Data shapes: Train={X_train.shape}, Val={X_val.shape}, Test={X_test.shape}")
    
    models = {
        "Naive Bayes": GaussianNB(),
        "Decision Tree": DecisionTreeClassifier(class_weight='balanced', max_depth=10, random_state=42),
        "Random Forest": RandomForestClassifier(class_weight='balanced', n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    }
    
    # Create output file
    report_path = 'model_metrics.txt'
    with open(report_path, 'w') as f:
        f.write("=== ML CONCEPT GAP PREDICTOR REPORT ===\n\n")
        f.write("NOTE: Models evaluated on synthetic data (simulated latent mastery). Results are experimental.\n\n")
        
        for name, model in models.items():
            print(f"Training {name}...")
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate on Validation Set for tuning info (Optional for demo)
            y_val_pred = model.predict(X_val)
            val_acc = accuracy_score(y_val, y_val_pred)
            
            # Final Evaluation on Held-out Test Set
            y_test_pred = model.predict(X_test)
            
            acc = accuracy_score(y_test, y_test_pred)
            prec = precision_score(y_test, y_test_pred, average='macro', zero_division=0)
            rec = recall_score(y_test, y_test_pred, average='macro', zero_division=0)
            f1 = f1_score(y_test, y_test_pred, average='macro', zero_division=0)
            cm = confusion_matrix(y_test, y_test_pred)
            
            res_str = (
                f"Model: {name}\n"
                f"Validation Accuracy: {val_acc:.4f}\n"
                f"Test Accuracy: {acc:.4f} ({(acc*100):.1f}%)\n"
                f"Macro Precision: {prec:.4f}\n"
                f"Macro Recall: {rec:.4f}\n"
                f"Macro F1-Score: {f1:.4f}\n"
                f"Confusion Matrix (first 4x4):\n{cm[:4,:4]}\n"
                "-"*40 + "\n"
            )
            print(res_str)
            f.write(res_str)
            
            # Save the trained model
            model_filename = f"{name.replace(' ', '_').lower()}.pkl"
            joblib.dump(model, model_filename)
            f.write(f"Saved model to {model_filename}\n\n")
            
        # Save feature column list for the demo script
        joblib.dump(list(X.columns), 'feature_columns.pkl')

if __name__ == '__main__':
    main()
