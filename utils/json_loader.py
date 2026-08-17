"""
Utility module for safely loading and caching static JSON knowledge files.
"""

import json
import os

_DATA_CACHE = {}

def get_data_dir():
    return os.path.join(os.path.dirname(__file__), "..", "data")

def load_json_file(relative_path, force_reload=False):
    """
    Loads a JSON file relative to the data/ directory with in-memory caching.
    """
    global _DATA_CACHE
    if not force_reload and relative_path in _DATA_CACHE:
        return _DATA_CACHE[relative_path]

    full_path = os.path.join(get_data_dir(), relative_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"JSON data file not found: {full_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    _DATA_CACHE[relative_path] = data
    return data

def get_all_careers():
    return load_json_file("careers.json")

def get_career_by_id(career_id):
    careers = get_all_careers()
    for c in careers:
        if c["id"] == career_id:
            return c
    return None

def get_career_questions():
    return load_json_file("career_questions.json")

def get_skills_data():
    return load_json_file("skills.json")

def get_roadmaps_data():
    return load_json_file("roadmaps.json")

def get_skill_test(test_id):
    filename = f"skill_tests/{test_id}.json"
    return load_json_file(filename)
