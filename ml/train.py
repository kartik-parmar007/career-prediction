"""
Model Training Script for AI IT Career Advisor.
Generates synthetic benchmark training dataset across 12 IT careers,
evaluates multiple classification algorithms (RandomForest, LogisticRegression, GradientBoosting),
computes comprehensive evaluation metrics, and persists the best model pipeline using Joblib.
"""

import os
import random
import numpy as np
import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from preprocessing import create_preprocessor, NUMERICAL_FEATURES, CATEGORICAL_FEATURES

# Define the 12 IT career archetypes and characteristic feature distributions
CAREER_PROFILES = {
    "frontend": {
        "math_enjoyment": (1, 3.5),
        "programming_enjoyment": (3.5, 5),
        "ui_design_enjoyment": (4, 5),
        "logic_problem_solving": (3, 4.5),
        "data_preference": (1, 3),
        "cloud_infra_enjoyment": (1, 3),
        "cybersecurity_enjoyment": (1, 3),
        "statistics_comfort": (1, 3),
        "debugging_enjoyment": (3, 4.5),
        "build_vs_analyze": ["build_user_facing", "build_user_facing", "build_systems"],
        "work_style_preference": ["visual_creative", "visual_creative", "logic_architecture"],
        "career_archetype": ["creative_visual", "creative_visual", "balanced_generalist"]
    },
    "backend": {
        "math_enjoyment": (2.5, 4.5),
        "programming_enjoyment": (4, 5),
        "ui_design_enjoyment": (1, 2.5),
        "logic_problem_solving": (4, 5),
        "data_preference": (3, 4.5),
        "cloud_infra_enjoyment": (3, 4.5),
        "cybersecurity_enjoyment": (2.5, 4),
        "statistics_comfort": (2, 4),
        "debugging_enjoyment": (3.5, 5),
        "build_vs_analyze": ["build_systems", "build_systems", "build_user_facing"],
        "work_style_preference": ["logic_architecture", "logic_architecture", "systems_reliability"],
        "career_archetype": ["technical_engineering", "technical_engineering", "balanced_generalist"]
    },
    "fullstack": {
        "math_enjoyment": (2.5, 4),
        "programming_enjoyment": (4, 5),
        "ui_design_enjoyment": (3.5, 4.5),
        "logic_problem_solving": (3.5, 5),
        "data_preference": (2.5, 4),
        "cloud_infra_enjoyment": (3, 4),
        "cybersecurity_enjoyment": (2.5, 3.8),
        "statistics_comfort": (2, 3.8),
        "debugging_enjoyment": (3.5, 4.8),
        "build_vs_analyze": ["build_user_facing", "build_systems"],
        "work_style_preference": ["visual_creative", "logic_architecture", "systems_reliability"],
        "career_archetype": ["balanced_generalist", "technical_engineering", "creative_visual"]
    },
    "mobile": {
        "math_enjoyment": (2, 3.8),
        "programming_enjoyment": (3.8, 5),
        "ui_design_enjoyment": (3.8, 5),
        "logic_problem_solving": (3.5, 4.5),
        "data_preference": (1.5, 3),
        "cloud_infra_enjoyment": (1.5, 3.2),
        "cybersecurity_enjoyment": (1.5, 3),
        "statistics_comfort": (1.5, 3),
        "debugging_enjoyment": (3, 4.5),
        "build_vs_analyze": ["build_user_facing", "build_user_facing", "build_systems"],
        "work_style_preference": ["visual_creative", "visual_creative", "logic_architecture"],
        "career_archetype": ["creative_visual", "technical_engineering"]
    },
    "data_analyst": {
        "math_enjoyment": (3, 4.5),
        "programming_enjoyment": (2, 3.8),
        "ui_design_enjoyment": (2.5, 4),
        "logic_problem_solving": (3.5, 5),
        "data_preference": (4.2, 5),
        "cloud_infra_enjoyment": (1, 2.5),
        "cybersecurity_enjoyment": (1, 2.5),
        "statistics_comfort": (3.5, 5),
        "debugging_enjoyment": (2.5, 4),
        "build_vs_analyze": ["analyze_data", "analyze_data", "research_models"],
        "work_style_preference": ["data_investigative", "data_investigative", "visual_creative"],
        "career_archetype": ["analytical_data", "analytical_data", "creative_visual"]
    },
    "data_scientist": {
        "math_enjoyment": (4, 5),
        "programming_enjoyment": (3.5, 5),
        "ui_design_enjoyment": (1.5, 3),
        "logic_problem_solving": (4.2, 5),
        "data_preference": (4.5, 5),
        "cloud_infra_enjoyment": (1.5, 3.5),
        "cybersecurity_enjoyment": (1.5, 3),
        "statistics_comfort": (4.5, 5),
        "debugging_enjoyment": (3, 4.5),
        "build_vs_analyze": ["research_models", "analyze_data", "research_models"],
        "work_style_preference": ["data_investigative", "data_investigative", "logic_architecture"],
        "career_archetype": ["analytical_data", "analytical_data", "technical_engineering"]
    },
    "ai_ml": {
        "math_enjoyment": (4.5, 5),
        "programming_enjoyment": (4.2, 5),
        "ui_design_enjoyment": (1, 2.5),
        "logic_problem_solving": (4.5, 5),
        "data_preference": (4, 5),
        "cloud_infra_enjoyment": (2.5, 4.2),
        "cybersecurity_enjoyment": (1.5, 3.2),
        "statistics_comfort": (4.2, 5),
        "debugging_enjoyment": (3.5, 5),
        "build_vs_analyze": ["research_models", "research_models", "build_systems"],
        "work_style_preference": ["data_investigative", "logic_architecture"],
        "career_archetype": ["analytical_data", "technical_engineering", "analytical_data"]
    },
    "devops_cloud": {
        "math_enjoyment": (1.5, 3.5),
        "programming_enjoyment": (3, 4.5),
        "ui_design_enjoyment": (1, 2),
        "logic_problem_solving": (3.8, 5),
        "data_preference": (2, 3.5),
        "cloud_infra_enjoyment": (4.5, 5),
        "cybersecurity_enjoyment": (3.5, 4.8),
        "statistics_comfort": (1.5, 3),
        "debugging_enjoyment": (4, 5),
        "build_vs_analyze": ["build_systems", "build_systems", "protect_test"],
        "work_style_preference": ["systems_reliability", "systems_reliability", "quality_adversarial"],
        "career_archetype": ["systems_security", "systems_security", "technical_engineering"]
    },
    "cybersecurity": {
        "math_enjoyment": (2, 3.8),
        "programming_enjoyment": (3, 4.5),
        "ui_design_enjoyment": (1, 2),
        "logic_problem_solving": (4, 5),
        "data_preference": (2.5, 4),
        "cloud_infra_enjoyment": (3.5, 4.8),
        "cybersecurity_enjoyment": (4.8, 5),
        "statistics_comfort": (2, 3.5),
        "debugging_enjoyment": (4, 5),
        "build_vs_analyze": ["protect_test", "protect_test", "build_systems"],
        "work_style_preference": ["quality_adversarial", "quality_adversarial", "systems_reliability"],
        "career_archetype": ["systems_security", "systems_security", "technical_engineering"]
    },
    "qa_automation": {
        "math_enjoyment": (1.5, 3.5),
        "programming_enjoyment": (3.2, 4.5),
        "ui_design_enjoyment": (2.5, 3.8),
        "logic_problem_solving": (3.8, 4.8),
        "data_preference": (2, 3.5),
        "cloud_infra_enjoyment": (2.5, 3.8),
        "cybersecurity_enjoyment": (2.5, 3.8),
        "statistics_comfort": (1.5, 3),
        "debugging_enjoyment": (4.5, 5),
        "build_vs_analyze": ["protect_test", "protect_test", "build_user_facing"],
        "work_style_preference": ["quality_adversarial", "quality_adversarial", "visual_creative"],
        "career_archetype": ["systems_security", "technical_engineering", "balanced_generalist"]
    },
    "ui_ux": {
        "math_enjoyment": (1, 2.5),
        "programming_enjoyment": (1, 2.8),
        "ui_design_enjoyment": (4.8, 5),
        "logic_problem_solving": (3, 4.2),
        "data_preference": (2, 3.5),
        "cloud_infra_enjoyment": (1, 2),
        "cybersecurity_enjoyment": (1, 2),
        "statistics_comfort": (1.5, 3),
        "debugging_enjoyment": (2, 3.5),
        "build_vs_analyze": ["build_user_facing", "build_user_facing", "analyze_data"],
        "work_style_preference": ["visual_creative", "visual_creative", "data_investigative"],
        "career_archetype": ["creative_visual", "creative_visual", "balanced_generalist"]
    },
    "data_engineer": {
        "math_enjoyment": (3, 4.5),
        "programming_enjoyment": (4, 5),
        "ui_design_enjoyment": (1, 2),
        "logic_problem_solving": (4.2, 5),
        "data_preference": (4.8, 5),
        "cloud_infra_enjoyment": (4, 5),
        "cybersecurity_enjoyment": (2.5, 3.8),
        "statistics_comfort": (2.5, 4),
        "debugging_enjoyment": (3.8, 5),
        "build_vs_analyze": ["build_systems", "analyze_data", "build_systems"],
        "work_style_preference": ["logic_architecture", "systems_reliability", "data_investigative"],
        "career_archetype": ["technical_engineering", "analytical_data", "systems_security"]
    }
}

TIME_OPTIONS = ["under_5_hrs", "5_to_10_hrs", "10_to_20_hrs", "20_plus_hrs"]
EXP_OPTIONS = ["none", "basics", "intermediate", "advanced"]
EDU_OPTIONS = ["high_school", "cs_degree", "non_cs_degree", "self_taught"]

def generate_synthetic_dataset(samples_per_career=150):
    """
    Generates a realistic synthetic tabular dataset for training the career recommendation model.
    Clearly structured as realistic demonstration baseline data.
    """
    rows = []
    for career, profile in CAREER_PROFILES.items():
        for _ in range(samples_per_career):
            row = {}
            for num_feat in NUMERICAL_FEATURES:
                min_v, max_v = profile[num_feat]
                # Gaussian sample around the target range with noise
                mean = (min_v + max_v) / 2.0
                std = (max_v - min_v) / 3.0
                val = np.clip(np.random.normal(mean, std), 1.0, 5.0)
                # Round to 1 decimal place or integer
                row[num_feat] = round(val, 1)

            row["build_vs_analyze"] = random.choice(profile["build_vs_analyze"])
            row["learning_time_commitment"] = random.choice(TIME_OPTIONS)
            row["programming_experience_level"] = random.choice(EXP_OPTIONS)
            row["education_background"] = random.choice(EDU_OPTIONS)
            row["work_style_preference"] = random.choice(profile["work_style_preference"])
            row["career_archetype"] = random.choice(profile["career_archetype"])
            row["target_career"] = career
            rows.append(row)

    df = pd.DataFrame(rows)
    return df

def train_and_evaluate():
    print("=" * 60)
    print("AI IT Career Advisor — Model Training Pipeline")
    print("=" * 60)

    # 1. Generate / Load dataset
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    dataset_path = os.path.join(data_dir, "career_dataset.csv")

    df = generate_synthetic_dataset(samples_per_career=160) # ~1920 samples
    df.to_csv(dataset_path, index=False)
    print(f"Generated synthetic training dataset: {dataset_path} ({len(df)} samples)")

    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    y = df["target_career"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    preprocessor = create_preprocessor()

    # 2. Candidate Models Comparison
    candidates = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=200, max_depth=12, min_samples_split=4, random_state=42),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    }

    best_name = None
    best_score = -1.0
    best_pipeline = None

    print("\n--- Evaluating Models (5-Fold Stratified CV) ---")
    for name, clf in candidates.items():
        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", clf)
        ])
        scores = cross_val_score(pipe, X_train, y_train, cv=5, scoring="accuracy")
        mean_score = scores.mean()
        print(f"[{name}] Mean CV Accuracy: {mean_score:.4f} (+/- {scores.std():.4f})")
        if mean_score > best_score:
            best_score = mean_score
            best_name = name
            best_pipeline = pipe

    print(f"\n>> Selected Best Model: {best_name} (CV Accuracy: {best_score:.4f})")

    # 3. Fit Best Model on Full Training Set and Evaluate on Test Set
    best_pipeline.fit(X_train, y_train)
    y_pred = best_pipeline.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    print("\n--- Final Test Set Evaluation ---")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")

    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, zero_division=0))

    # 4. Save the trained pipeline
    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    joblib.dump(best_pipeline, model_path)
    print(f"\nSuccessfully persisted model artifact to: {model_path}")
    print("=" * 60)

if __name__ == "__main__":
    train_and_evaluate()
