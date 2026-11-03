import os

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify(message="Welcome to the DevOps CI/CD demo service!")


@app.route("/health")
def health():
    return jsonify(status="healthy"), 200


if __name__ == "__main__":
    # Listen on all interfaces so the app is reachable from outside the container.
    # The port comes from the PORT environment variable, defaulting to 5000.
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
