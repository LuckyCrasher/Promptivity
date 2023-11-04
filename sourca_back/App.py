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
import g4f

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


def genEmail(mostUseWeb, mostUsedReaosn):
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
    body = greeting + "\n" + webStatement + "\n" + reasonStatement + "\n"
    return body


def compute_stats():
    with app.app_context():
        querry_num_websites = db.session.execute(text("SELECT hostname, COUNT(hostname) as num FROM Records GROUP BY hostname ORDER BY num DESC LIMIT 3"))
        most_used_sites = querry_num_websites.fetchall()

    with app.app_context():
        querry_common_reasons = db.session.execute(text("SELECT prompt, COUNT(prompt) as num FROM Records GROUP BY prompt ORDER BY num DESC LIMIT 3"))
        most_common_prompts = querry_common_reasons.fetchall()
    return most_used_sites, most_common_prompts


def getAllData():
    with app.app_context():
        query = db.session.execute(text("SELECT hostname, prompt from Records"))
    return query.fetchall()


def ask_chatgpt():
    # Define the extended dataset
    suggested_email = """(Hello, 
                       I am Promptivity and I will provide your recent internet activity to help you better understand your online habits.)
                       Below is a summary of the time spent most time on:
                       - {Website 1}: _ amount visited
                       - {Website 2}: _ amount visited
                       - {Website 3}: _ amount visited
                       The most common reasons you gave to visit those sites:
                       - {Reason 1}: _ amount used 
                       - {Reason 2}: _ amount used 
                       - {Reason 3}: _ amount used 
                       Short Recommendations about productivity and about spending time wisely
                       Thank you for using Promptivity, Have a great day! 😊"""

    # Function to convert time to minutes
    #def convert_to_minutes(time_str):
    #    if 'hour' in time_str:
    #        hours = float(time_str.split(' hour')[0])
    #        total_minutes = int(hours * 60)
    #    else:
    #        total_minutes = int(time_str.split(' minute')[0])
    #    return total_minutes

    # Convert the Duration column to minutes
    #extended_dataset['Duration'] = extended_dataset['Duration'].apply(convert_to_minutes)

    # Group by Reason and aggregate
    #aggregated_data = extended_dataset.groupby('Reason').agg({
    #    'Duration': 'sum'
    #}).reset_index()

    # Convert the aggregated duration back to a more readable format (hours and minutes)
    #aggregated_data['Duration'] = aggregated_data['Duration'].apply(lambda x: f"{x // 60} hours {x % 60} minutes")

    # Create a string representation of the aggregated data
    aggregated_str = str(getAllData())

    # Construct the prompt
    prompt = f"""
    Write the email about to a user about the time spent on these websites and give suggestions. Here are the data:
    {aggregated_str}. You don't have to write about all, just make a summary most used websites and reasons. 
    Mention about good and bad habits. Write a very friendly email, do not be like AI. 
    Don't ask questions. Make it short. My name is Promptivity, mention you are going to provide the internet activity. 
    Don't include sources at the end and you cannot provide further details.Use {suggested_email} as the outline
    """

    # Use g4f to generate the email summary
    try:
        email_response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": prompt}],
        )
        # Print the generated email content
        return email_response
    except Exception as e:
        print(f"An error occurred: {e}")
    return None


def handle_sendmail(thread_num, email):
    print(f"Thread {thread_num}: starting")
    most_common_website, most_common_reason = compute_stats()
    chat_gpt = ask_chatgpt()
    if chat_gpt is None:
        chat_gpt = genEmail(most_common_website, most_common_reason)
    sendEmail(chat_gpt, email)
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
