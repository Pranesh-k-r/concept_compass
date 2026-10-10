# ML-Based Improvement Suggestions Feature

This is a standalone Machine Learning experiment designed to predict a student's concept gaps and recommend personalized learning activities based on their diagnostic quiz performance. 

It is entirely isolated from the main Concept Compass Django application.

## Contents
- `train.py`: The pipeline for data engineering, model training, hyperparameter tuning, and evaluation.
- `recommender.py`: The logic mapping predicted concept gaps to readable improvement reports.
- `demo.py`: A standalone demonstration script showing a mock student predicting a gap and generating an improvement report.

## How to run the experiment independently

### 1. Train the Models
First, run the training pipeline. This will read the synthetic dataset in read-only mode, train three models (Naive Bayes, Decision Tree, Random Forest), evaluate them, and output a detailed `evaluation_report.txt` and `.pkl` model files.

```bash
cd ml_experiments/improvement_suggestions/
python train.py
```

### 2. Run the Demo
Once the models are trained and saved, run the demo to simulate a student's input and generate an Improvement Report:

```bash
python demo.py
```

## Note on Synthetic Data Limitations
The evaluation results contained within `evaluation_report.txt` are based on a synthetic benchmarking dataset. Because the dataset provides only extremely sparse, flattened snapshots of responses (~20 binary indicators per student), traditional ML models max out in the low 20% range for accuracy. 
Do not use these models on real students without gathering denser, longitudinal interaction data first.
