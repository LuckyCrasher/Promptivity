from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

submissions_storage = []

@app.route('/validate-reason', methods=['POST'])
def validate_reason():
    content = request.json
    print(type(content))
    print(content)
    if not content or 'reason' not in content:
        return jsonify({"error": "No reason provided"}), 400
    try:
        #reason = content['reason']
        return jsonify({"reason": "reason", "is_valid": True}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/get-submissions', methods=['GET'])
def get_submissions():
    return jsonify(submissions_storage), 200

if __name__ == '__main__':
    app.run(debug=True)
