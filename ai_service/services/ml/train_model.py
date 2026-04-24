
import numpy as np
from sklearn.linear_model import LogisticRegression
import pickle

X = np.array([
    [3, 300, 4],
    [1, 50, 0],
    [4, 400, 5],
    [2, 80, 1],
])

y = np.array([1, 0, 1, 0])

model = LogisticRegression()
model.fit(X, y)

with open("ml/confidence_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model trained!")