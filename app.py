import os
from flask import Flask, request, jsonify
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
app = Flask(__name__)

@app.route("/studybuddy/search", methods=["POST"])
def studybuddy_search():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer ") or auth.split(" ", 1)[1] != os.environ["ACTION_API_KEY"]:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True)
    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Missing query"}), 400

    try:
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {"role": "system", "content": "You are a helpful study buddy."},
                {"role": "user", "content": query},
            ],
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [os.environ["VECTOR_STORE_ID"]]
                }
            },
        )
        text = response.output_text or "(no content)"
        return jsonify({"answer": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 502