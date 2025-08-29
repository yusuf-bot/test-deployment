from flask import Flask, request, jsonify
from mistral_client import client, websearch_agent

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")

    # Start a conversation with the agent
    response = client.beta.conversations.start(
        agent_id=websearch_agent.id,
        inputs=[{"role": "user", "content": user_msg}]
    )

    # Extract assistant reply
    try:
        reply = response.outputs[0].content[0].text
    except Exception:
        reply = "Sorry, I couldn’t process that."

    return jsonify({"reply": respons`e})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
