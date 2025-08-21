import os
from flask import Flask, request, jsonify
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
app = Flask(__name__)

@app.route("/studybuddy/search", methods=["POST"])
def studybuddy_search():
    # ✅ Log request source and payload
    print("📥 /studybuddy/search hit")
    
    data = request.get_json(force=True)
    query = (data.get("query") or "").strip()

    if not query:
        return jsonify({"error": "Missing 'query'"}), 400

    # ✅ Log the query
    print(f"🔍 Received query: {query}")

    try:
        # ✅ Run the actual OpenAI Responses API call with file_search
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

        # ✅ Grab the result
        text = response.output_text or "(no content returned)"
        return jsonify({"answer": text})

    except Exception as e:
        print("❌ Error during OpenAI call:", str(e))
        return jsonify({
            "error": "Upstream failure",
            "detail": str(e)
        }), 502

# Optional health route
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})