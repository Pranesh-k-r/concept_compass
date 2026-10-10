import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

def main():
    print("Loading data...")
    # Load data
    profiles_df = pd.read_csv('../Datasets/annotated_profiles.csv')
    responses_df = pd.read_csv('../Datasets/student_responses.csv')
    
    # Feature Engineering
    # We want to predict annotated_root_gap_concept_id for a given profile
    print("Engineering features...")
    
    # Pivot responses to get accuracy per concept per profile
    # For this dataset, each row is a question response.
    # Group by profile_id and concept_id, calculate mean of is_correct
    concept_acc = responses_df.groupby(['profile_id', 'concept_id'])['is_correct'].mean().unstack()
    
    # Fill missing values. -1 means the concept was not assessed for this profile
    concept_acc = concept_acc.fillna(-1)
    
    # Also add time_seconds and hints_used if useful, maybe mean per concept
    time_spent = responses_df.groupby(['profile_id', 'concept_id'])['time_seconds'].mean().unstack().fillna(-1)
    time_spent.columns = [f"{c}_time" for c in time_spent.columns]
    
    # Merge with target labels
    data = profiles_df[['profile_id', 'annotated_root_gap_concept_id']].set_index('profile_id')
    
    # Combine features
    X = concept_acc.join(time_spent, how='inner')
    y = data.loc[X.index, 'annotated_root_gap_concept_id']
    
    # Drop classes with too few samples if necessary, but here we can keep all
    print(f"Data shape: X={X.shape}, y={y.shape}")
    
    # Train test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    models = {
        "Naive Bayes": GaussianNB(),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(random_state=42)
    }
    
    # Hyperparameters for grid search
    param_grids = {
        "Naive Bayes": {
            'var_smoothing': np.logspace(0,-9, num=10)
        },
        "Logistic Regression": {
            'C': [0.1, 1, 10]
        },
        "Random Forest": {
            'n_estimators': [50, 100],
            'max_depth': [None, 10, 20]
        }
    }
    
    results = []
    
    with open('report.txt', 'w') as f:
        f.write("--- ML EXPERIMENT RESULTS ---\n")
        f.write("Baseline (Rule-based) accuracy on subset: 18.6%\n\n")
        
        for name, model in models.items():
            print(f"Training {name}...")
            
            clf = GridSearchCV(model, param_grids[name], cv=3, n_jobs=-1, scoring='accuracy')
            clf.fit(X_train, y_train)
            
            best_model = clf.best_estimator_
            y_pred = best_model.predict(X_test)
            
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, average='macro', zero_division=0)
            rec = recall_score(y_test, y_pred, average='macro', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
            cm = confusion_matrix(y_test, y_pred)
            
            res_str = (
                f"Model: {name}\n"
                f"Best Params: {clf.best_params_}\n"
                f"Test Accuracy: {acc:.4f} ({(acc*100):.1f}%)\n"
                f"Macro Precision: {prec:.4f}\n"
                f"Macro Recall: {rec:.4f}\n"
                f"Macro F1-Score: {f1:.4f}\n"
                f"Confusion Matrix snippet (first 3x3):\n{cm[:3,:3]}\n"
                "-"*40 + "\n"
            )
            print(res_str)
            f.write(res_str)
            
            # Save model
            model_filename = f"{name.replace(' ', '_').lower()}_model.pkl"
            joblib.dump(best_model, model_filename)
            f.write(f"Saved model to {model_filename}\n\n")

if __name__ == '__main__':
    main()
