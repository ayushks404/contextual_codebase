# ml/model.py

import pickle
import numpy as np
import os 

MODEL_PATH = "services/ml/confidence_model.pkl"

model = None

def load_model():
    global model
    if model is None:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)

def predict_confidence(features):
    num_chunks, answer_length, keyword_overlap = features

    score = 0

    if num_chunks >= 3:
        score += 0.3

    if answer_length > 200:
        score += 0.3

    if keyword_overlap >= 2:
        score += 0.4

    return round(score, 2)