"""
Preprocessing module for Career Recommendation ML pipeline.
Handles feature extraction, categorical encodings, scaling, and feature names.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

# Numerical features (scale 1-5)
NUMERICAL_FEATURES = [
    "math_enjoyment",
    "programming_enjoyment",
    "ui_design_enjoyment",
    "logic_problem_solving",
    "data_preference",
    "cloud_infra_enjoyment",
    "cybersecurity_enjoyment",
    "statistics_comfort",
    "debugging_enjoyment"
]

# Categorical features
CATEGORICAL_FEATURES = [
    "build_vs_analyze",
    "learning_time_commitment",
    "programming_experience_level",
    "education_background",
    "work_style_preference",
    "career_archetype"
]

ALL_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES

def create_preprocessor():
    """
    Creates a scikit-learn ColumnTransformer preprocessor.
    """
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, NUMERICAL_FEATURES),
            ('cat', categorical_transformer, CATEGORICAL_FEATURES)
        ]
    )
    return preprocessor

def prepare_input_dataframe(answers_dict):
    """
    Validates and converts a raw questionnaire answers dictionary into a 1-row DataFrame.
    """
    row = {}
    for num_col in NUMERICAL_FEATURES:
        val = answers_dict.get(num_col, 3)
        try:
            row[num_col] = float(val)
        except (ValueError, TypeError):
            row[num_col] = 3.0

    for cat_col in CATEGORICAL_FEATURES:
        row[cat_col] = str(answers_dict.get(cat_col, "unknown"))

    return pd.DataFrame([row])
