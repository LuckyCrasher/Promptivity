from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import spacy

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")
CORS(app)

submissions_storage = []



@app.route('/validate-reason', methods=['POST'])
def validate_reason():
    content = request.json
    print(type(content))
    print(content)
    if not content or 'reason' not in content:
        return jsonify({"error": "No reason provided"}), 400
    
    reason = content['reason']
    if is_valid_response(reason):
        return jsonify({"reason": reason, "is_valid": True}), 200
    else:
        return jsonify({"error": "Invalid response or no verb in the response"}, 400)

def is_valid_response(text):
    doc = nlp(text)

    # Define the allowed part-of-speech tags, including gerunds (VERB and PART)
    allowed_tags = {"NOUN", "VERB", "ADJ", "ADV", "INTJ", "PRON", "PART"}

    # Check if there is at least one token with an allowed part-of-speech tag
    contains_allowed_tag = any(token.pos_ in allowed_tags for token in doc)

    return contains_verb(text) and contains_allowed_tag

def contains_verb(text):
    doc = nlp(text)

    # Check if there is at least one verb in the text
    return any(token.pos_ == "VERB" for token in doc)

@app.route('/get-submissions', methods=['GET'])
def get_submissions():
    return jsonify(submissions_storage), 200

if __name__ == '__main__':
    app.run(debug=True)
