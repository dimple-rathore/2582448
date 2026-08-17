import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:1b"


def generate_explanation(
    room_id,
    building,
    floor,
    capacity,
    distance,
    capacity_score,
    facility_score,
    required_facilities
):
    prompt = f"""
You are a university classroom allocation assistant.

Write a short, professional explanation of why classroom {room_id} was recommended.

Classroom information:
- Building: {building}
- Floor: {floor}
- Capacity: {capacity}
- Distance category: {distance}
- Required facilities: {required_facilities}

Explain the recommendation using only these facts.

Rules:
- Mention that the classroom matches the required capacity.
- Mention that it provides the requested facilities.
- Mention the distance category only if useful.
- Do not invent any facilities or other information.
- Do not assign units to the distance.
- Do not say that distance affects capacity or facilities.
- Do not mention scores.
- Do not make comparisons with other classrooms.
- Do not use conversational phrases.
- Write exactly 2 concise sentences.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        response.raise_for_status()

        return response.json()["response"].strip()

    except Exception as e:
        return (
            "AI explanation could not be generated. "
            f"Please check that Ollama is running. ({e})"
        )