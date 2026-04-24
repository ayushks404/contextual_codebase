# graph/workflow.py

from agents.answer_agent import answer_agent
from agents.critic import critic_agent
from ml.feature_extractor import extract_features
from ml.model import predict_confidence


def run_workflow(project_id, query):
    state = {
        "project_id": project_id,
        "query": query,
        "iterations": 0
    }

    while True:
        # Step 1: Generate Answer
        state.update(answer_agent(state))

        # Step 2: Extract Features
        features_data = extract_features(state)
        state["features"] = features_data["features"]

        # Step 3: Predict Confidence
        confidence = predict_confidence(state["features"])
        state["confidence"] = confidence

        # Step 4: Critic Decision
        decision = critic_agent(state)

        if decision["action"] == "accept":
            break

        state["iterations"] = decision["iterations"]

    return {
        "answer": state["answer"],
        "confidence": state["confidence"]
    }