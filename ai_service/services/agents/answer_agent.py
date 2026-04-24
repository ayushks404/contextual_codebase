# agents/answer_agent.py

from rag.rag_engine import answer_question

def answer_agent(state):
    project_id = state["project_id"]
    query = state["query"]

    result = answer_question(project_id, query)

    return {
        "answer": result.get("answer")
    }