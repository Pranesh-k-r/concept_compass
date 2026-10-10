import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def main():
    print("Loading datasets in read-only mode...")
    profiles_df = pd.read_csv('../../Datasets/annotated_profiles.csv')
    responses_df = pd.read_csv('../../Datasets/student_responses.csv')
    
    print("Engineering features...")
    concept_acc = responses_df.groupby(['profile_id', 'concept_id'])['is_correct'].mean().unstack()
    concept_acc.columns = [f"{c}_correct" for c in concept_acc.columns]
    
    time_spent = responses_df.groupby(['profile_id', 'concept_id'])['time_seconds'].mean().unstack()
    time_spent.columns = [f"{c}_time" for c in time_spent.columns]
    
    hints = responses_df.groupby(['profile_id', 'concept_id'])['hints_used'].mean().unstack()
    hints.columns = [f"{c}_hints" for c in hints.columns]
    
    data = profiles_df[['profile_id', 'annotated_root_gap_concept_id']].set_index('profile_id')
    
    # Missing values mean unattempted, filled with -1
    X = pd.concat([concept_acc, time_spent, hints], axis=1).fillna(-1)
    y = data.loc[X.index, 'annotated_root_gap_concept_id']
    
    # Leakage-safe split: Stratified by target across profile rows
    X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)
    
    print(f"Data shapes: Train/Val={X_train_val.shape}, Test={X_test.shape}")
    
    majority_class = y_train_val.mode()[0]
    baseline_acc = (y_test == majority_class).mean()
    
    models = {
        "Naive Bayes": {
            "model": GaussianNB(),
            "params": {'var_smoothing': [1e-9, 1e-8]}
        },
        "Decision Tree": {
            "model": DecisionTreeClassifier(class_weight='balanced', random_state=42),
            "params": {'max_depth': [10, 20, None], 'min_samples_split': [2, 5]}
        },
        "Random Forest": {
            "model": RandomForestClassifier(class_weight='balanced', random_state=42, n_jobs=-1),
            "params": {'n_estimators': [50, 100], 'max_depth': [10, 20]}
        }
    }
    
    report_path = 'evaluation_report.txt'
    best_model_overall = None
    best_acc = -1
    
    with open(report_path, 'w') as f:
        f.write("=== ML IMPROVEMENT SUGGESTIONS PREDICTOR REPORT ===\n\n")
        f.write("DATASET: Synthetic Latent Mastery Benchmark (not real-world pedagogical performance).\n\n")
        f.write(f"Baseline (Majority Class '{majority_class}') Accuracy: {baseline_acc:.4f} ({(baseline_acc*100):.1f}%)\n")
        f.write("-" * 50 + "\n\n")
        
        for name, config in models.items():
            print(f"Tuning and Training {name}...")
            
            # GridSearchCV uses internal K-Fold validation on X_train_val for hyperparameter tuning
            clf = GridSearchCV(config["model"], config["params"], cv=3, scoring='accuracy')
            clf.fit(X_train_val, y_train_val)
            
            best_model = clf.best_estimator_
            y_pred = best_model.predict(X_test)
            
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, average='macro', zero_division=0)
            rec = recall_score(y_test, y_pred, average='macro', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
            cm = confusion_matrix(y_test, y_pred)
            
            if acc > best_acc:
                best_acc = acc
                best_model_overall = (name, best_model)
            
            res_str = (
                f"Model: {name}\n"
                f"Best Params: {clf.best_params_}\n"
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
            joblib.dump(best_model, model_filename)
            f.write(f"Saved model to {model_filename}\n\n")
            
        f.write(f"\nOVERALL BEST MODEL: {best_model_overall[0]} with Accuracy {best_acc:.4f}\n")
        f.write("\nLIMITATIONS:\n")
        f.write("As established in previous experiments, the extreme sparsity of the synthetic interaction data (~20 questions per student) limits accuracy to ~23%. Sequence models and denser longitudinal data would be necessary for higher accuracy in a production environment.\n")

        # Save feature column list
        joblib.dump(list(X.columns), 'feature_columns.pkl')

if __name__ == '__main__':
    main()
