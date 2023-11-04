import atexit
import datetime
import threading
from email.message import EmailMessage
from urllib.parse import urlparse

from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

import smtplib#email
from email.mime.text import MIMEText#email
from email.mime.multipart import MIMEMultipart#email

senderEmail = "Promptivity@hotmail.com"
senderPassword = "BlueLight123"

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")
CORS(app)

running_threads = []

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
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow(), primary_key=True, nullable=False)
    hostname = db.Column(db.String(255), nullable=False)
    prompt = db.Column(db.String(255), nullable=False)

    def __init__(self, timestamp, hostname, prompt):
        self.timestamp = timestamp
        self.hostname = hostname
        self.prompt = prompt

    def __repr__(self):
        return f'<Records{self.timestamp} - {self.hostname} - {self.prompt}>'


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
            timestamp=datetime.datetime.now(),  # You need to import datetime
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


def sendEmail(body, email):
    message = EmailMessage()
    message['From'] = senderEmail
    message['To'] = email
    message['Subject'] = 'Promptivity Report'

    message.set_content(body)
    print(message.as_string())

    try:
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)  # Change to your SMTP server
        server.starttls()
        server.login(senderEmail, senderPassword)
        server.sendmail(senderEmail, email, message.as_string())
        print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print("Error: Unable to send email.", e)
    finally:
        server.quit()


def genEmail(mostUseWeb, mostUsedReaosn, suggestion):
    webStatement = "Your top three used websites were: \n"
    i = 1
    for website in mostUseWeb:
        site, num = website
        webStatement += f"{i}. {site} visited {num} times\n"
        i += 1

    reasonStatement = "Your most used reasons were: \n"

    i = 1
    for reason in mostUsedReaosn:
        reason, num = reason
        reasonStatement += f"{i}. {reason} given {num} times \n"
        i += 1

    greeting = "Hey there,"
    body = greeting + "\n" + webStatement + "\n" + reasonStatement + "\n" + suggestion
    return body


def compute_stats():
    with app.app_context():
        querry_num_websites = db.session.execute(text("SELECT hostname, COUNT(hostname) as num FROM Records GROUP BY hostname ORDER BY num DESC LIMIT 3"))
        most_used_sites = querry_num_websites.fetchall()

    with app.app_context():
        querry_common_reasons = db.session.execute(text("SELECT prompt, COUNT(prompt) as num FROM Records GROUP BY prompt ORDER BY num DESC LIMIT 3"))
        most_common_prompts = querry_common_reasons.fetchall()
    return most_used_sites, most_common_prompts


def ask_chatgpt():
    return "THIS IS FROM CHAT GPT"


def handle_sendmail(thread_num, email):
    print(f"Thread {thread_num}: starting")
    most_common_website, most_common_reason = compute_stats()
    email_body = genEmail(most_common_website, most_common_reason, ask_chatgpt())
    sendEmail(email_body, email)
    print(f"Thread {thread_num}: finishing")
    running_threads.pop(thread_num)


@app.route('/sendmail', methods=['POST'])
def get_sendmail():
    content = request.json
    if not content:
        return jsonify({"error": "No content provided"}), 400

    if 'email' not in content:
        return jsonify({"error": "No email provided"}), 400

    email = content['email']
    t = threading.Thread(target=handle_sendmail, args=(len(running_threads), email,))
    t.start()
    running_threads.append(t)

    return jsonify({"reason": "worked", "email": email}), 200


@app.route('/get-submissions', methods=['GET'])
def get_submissions():
    return jsonify(submissions_storage), 200


def close_running_threads():
    print("awaiting running threads")
    for thread in running_threads:
        thread.join()
    print("Threads complete, ready to finish")


def main():
    atexit.register(close_running_threads)
    with app.app_context():
        db.create_all()
    app.run(debug=True)


if __name__ == '__main__':
    main()
