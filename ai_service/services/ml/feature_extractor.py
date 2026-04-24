def extract_features(state):
    query = state["query"]
    answer = state["answer"]
    docs = state.get("docs", [])

    num_chunks = len(docs)
    answer_length = len(answer)

    keyword_overlap = sum(
        1 for word in query.split()
        if word.lower() in answer.lower()
    )

    return {
        "features": [
            num_chunks,
            answer_length,
            keyword_overlap
        ]
    }