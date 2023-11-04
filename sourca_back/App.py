from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

# Ensure the OPENAI_API_KEY environment variable is set
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

submissions_storage = []

@app.route('/validate-reason', methods=['POST'])
def validate_reason():
    content = request.json
    if not content or 'reason' not in content:
        return jsonify({"error": "No reason provided"}), 400

    reason = content['reason']
    if not isinstance(reason, str) or not reason.strip():
        return jsonify({"error": "Reason is not a valid string"}), 400

    try:
        response = openai.Completion.create(
            model="text-davinci-004",  # Replace with the appropriate model
            prompt=f"Is '{reason}' a valid reason for visiting a website?",
            max_tokens=50
        )

        validation_response = response.choices[0].text.strip()
        is_valid = "yes" in validation_response.lower()

        submissions_storage.append({"reason": reason, "is_valid": is_valid})

        return jsonify({"reason": reason, "is_valid": is_valid}), 200
    except Exception as e:
        # Log the exception here
        return jsonify({"error": str(e)}), 500

@app.route('/get-submissions', methods=['GET'])
def get_submissions():
    return jsonify(submissions_storage), 200

if __name__ == '__main__':
    app.run(debug=True)
