import datetime
from urllib.parse import urlparse

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import spacy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import sqlite3

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")
CORS(app)

submissions_storage = []
# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy()
# change string to the name of your database; add path if necessary
db_name = 'promptivity.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# initialize the app with Flask-SQLAlchemy
db.init_app(app)


class Records(db.Model):
    TimeStamp = db.Column(db.DateTime, default=datetime.datetime.utcnow(), primary_key=True, nullable=False)
    hostname = db.Column(db.String(255), nullable=False)
    prompt = db.Column(db.String(255), nullable=False)

    def __init__(self, time_stamp, hostname, prompt):
        self.TimeStamp = time_stamp
        self.hostname = hostname
        self.prompt = prompt

    def __repr__(self):
        return f'<YourModel {self.TimeStamp}>'


# NOTHING BELOW THIS LINE NEEDS TO CHANGE
# this route will test the database connection - and nothing more
@app.route('/testdb')
def testdb():
    try:
        db.session.query(text('1')).from_statement(text('SELECT 1')).all()
        results = db.session.execute(db.select(Records))
        return f'<h1>It works.</h1><br><p>{results.all()}</p>'
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


@app.route('/validate-reason', methods=['POST'])
def validate_reason():
    content = request.json
    if not content:
        return jsonify({"error": "No content provided"}), 400

    if 'reason' not in content:
        return jsonify({"error": "No reason provided"}), 400

    if 'url' not in content:
        return jsonify({"error": "No url provided"}), 400

    reason = content['reason']
    url = content['url']
    try:
        print(reason, url)
        parsed_uri = urlparse(url)
        result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        print(parsed_uri.hostname)

        new_data = Records(
            time_stamp=datetime.datetime.now(),  # You need to import datetime
            hostname=parsed_uri.hostname,
            prompt=reason
        )
        db.session.add(new_data)
        db.session.commit()
        if is_valid_response(reason):
            return jsonify({"reason": reason, "url": result, "is_valid": True}), 200
        else:
            return jsonify({"error": "Invalid response or no verb in the response"}, 400)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


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


def main():
    with app.app_context():
        db.create_all()
    app.run(debug=True)


if __name__ == '__main__':
    main()
