import atexit
import datetime
import threading
import uuid
from email.message import EmailMessage
from typing import Literal
from urllib.parse import urlparse

import matplotlib.pyplot as plt
from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import text
import g4f
from email.mime.image import MIMEImage  # Import MIMEImage
import graph

import smtplib  # email
from email.mime.text import MIMEText  # email
from email.mime.multipart import MIMEMultipart  # email

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

Action = Literal["start", "end"]


class Sessions(db.Model):
    __tablename__ = "sessions"
    sessionID: Mapped[str] = db.Column(db.String(36), primary_key=True, nullable=False)
    hostname: Mapped[str] = mapped_column(db.String, nullable=False)
    prompt: Mapped[str] = mapped_column(db.String, nullable=False)

    @staticmethod
    def create_session(sessionID, hostname, prompt):
        new_session = Sessions(sessionID=sessionID, hostname=hostname, prompt=prompt)
        db.session.add(new_session)
        db.session.commit()

    def __init__(self, sessionID, hostname, prompt):
        self.sessionID = sessionID
        self.hostname = hostname
        self.prompt = prompt

    def __repr__(self):
        return f'<Records{self.timestamp} - {self.hostname} - {self.prompt}>\n'


class Records(db.Model):
    __tablename__ = "records"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True, nullable=False)
    sessionID: Mapped[str] = db.Column(db.String(36), db.ForeignKey('sessions.sessionID'), nullable=False)
    timestamp: Mapped[db.DateTime] = mapped_column(db.DateTime, default=datetime.datetime.utcnow(), nullable=False)
    action: Mapped[Action] = mapped_column(db.String(10), nullable=False)
    session = db.relationship('Sessions', backref='records')

    @staticmethod
    def create_record(session, action):
        new_record = Records(sessionID=session, timestamp=datetime.datetime.utcnow(), action=action)
        db.session.add(new_record)
        db.session.commit()
        return new_record

    def __init__(self, sessionID, timestamp, action):
        self.sessionID = sessionID
        self.timestamp = timestamp
        self.action = action
        pass

    def __repr__(self):
        return f"<Record {self.id} - {self.sessionID} - {self.timestamp} - {self.action}>\n"


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


@app.route('/getrecords')
def getrecords():
    try:
        results = db.session.execute(text("SELECT * FROM Records"))
        return f'<h1>It works.</h1><br><p>{results.all()}</p>'
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


@app.route('/new-record', methods=['POST'])
def add_record():
    content = request.json
    if not content:
        return jsonify({"error": "No content provided"}), 400

    if 'sessionID' not in content:
        return jsonify({"error": "No sessionID provided"}), 400

    if 'action' not in content:
        return jsonify({"error": "No action provided"}), 400

    sessionID = content['sessionID']
    action = content['action']
    if action in Action.__args__:
        print(f"added record {sessionID} - {action}")
        Records.create_record(sessionID, action)
        return jsonify({"sessionID": sessionID, "action": action, "success": True}), 200
    return jsonify({"error": "Invalid request no action given"}, 400)


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

        sessionID = str(uuid.uuid4())
        print(type(sessionID))
        print(sessionID)
        Sessions.create_session(sessionID, parsed_uri.hostname, reason)
        Records.create_record(sessionID, "start")
        print("OKAY")
        if is_valid_response(reason):
            return jsonify({"sessionID": sessionID, "reason": reason, "url": result, "is_valid": True}), 200
        else:
            return jsonify({"error": "Invalid response or no verb in the response", "reason": reason, "url": result,
                            "is_valid": False}, 400)
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


def sendEmail(body, email, bar_graph_path, pie_chart_path):
    message = MIMEMultipart()
    message['From'] = senderEmail
    message['To'] = email
    message['Subject'] = 'Promptivity Report'

    message.attach(MIMEText(body, 'plain'))

    # Attach the bar graph
    with open(bar_graph_path, 'rb') as file:
        img = MIMEImage(file.read())
        img.add_header('Content-Disposition', f'attachment; filename="{bar_graph_path}"')
        message.attach(img)

    # Attach the pie chart
    with open(pie_chart_path, 'rb') as file:
        img = MIMEImage(file.read())
        img.add_header('Content-Disposition', f'attachment; filename="{pie_chart_path}"')
        message.attach(img)



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


def format_duration(seconds):
    if seconds < 60:
        return f"{format(seconds, '.2f')} second{'s' if seconds > 1 else ''}"
    elif seconds < 3600:
        minutes, remainder = divmod(seconds, 60)
        return f"{format(minutes, '.0f')} minute{'s' if minutes > 1 else ''} and {format(seconds, '.2f')} second{'s' if remainder > 1 else ''}"
    elif seconds < 86400:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{format(hours, '.2f')} hour{'s' if hours > 1 else ''}, {format(minutes, '.2f')} minute{'s' if minutes > 1 else ''}, and {format(seconds, '.2f')} second{'s' if seconds > 1 else ''}"
    else:
        duration = datetime.timedelta(seconds=seconds)
        return str(duration)


def genEmail(mostUseWeb, mostUsedReaosn, duration_on_site):
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

    reasonStatement = "The amount of time you spent: \n"
    i = 1
    for site, duartion in duration_on_site:
        reasonStatement += f"{i}. {site} given {format_duration(duartion)} \n"
        i += 1

    greeting = "Hey there,"
    body = greeting + "\n" + webStatement + "\n" + reasonStatement + "\n"
    return body


def compute_stats():
    with app.app_context():
        querry_num_websites = db.session.execute(
            text("SELECT hostname, COUNT(hostname) as num FROM sessions GROUP BY hostname ORDER BY num DESC LIMIT 3"))
        most_used_sites = querry_num_websites.fetchall()

    with app.app_context():
        querry_common_reasons = db.session.execute(
            text("SELECT prompt, COUNT(prompt) as num FROM sessions GROUP BY prompt ORDER BY num DESC LIMIT 3"))
        most_common_prompts = querry_common_reasons.fetchall()

    select_query = """
        SELECT hostname, SUM(duration) AS duration
        FROM (
            SELECT hostname,
                (ROUND((JULIANDAY(r2.timestamp) - JULIANDAY(r1.timestamp)) * 86400, 2)) AS duration
            FROM sessions
                JOIN records r1
                    ON sessions.sessionID = r1.sessionID
                        AND r1.action = 'start'
                        AND r1.timestamp > DATETIME('now', '-6 days')
                JOIN records r2
                    ON sessions.sessionID = r2.sessionID
                        AND r2.action = 'end'
                        AND r2.timestamp > DATETIME('now', '-6 days')
                        AND r1.timestamp < r2.timestamp
            GROUP BY r1.timestamp, hostname
        )
        GROUP BY hostname
        ORDER BY duration DESC;
        """
    with app.app_context():
        query = db.session.execute(text(select_query))
        duration_on_site = query.fetchall()

    return most_used_sites, most_common_prompts, duration_on_site


@app.route("/compute-stats")
def get_data_analysis():
    most_common_sites, most_used_prompts, amount_of_time = compute_stats()

    return jsonify({"data": {
        "most_common_sites": str(most_common_sites),
        "most_used_prompts": str(most_used_prompts),
        "duration_spent": str(amount_of_time)
    }}), 200


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
                       The amount of time spent on various websites:
                       - {Website 1}: _ duration spent 
                       - {Website 2}: _ duration spent
                       - {Website 3}: _ duration spent
                       Short Recommendations about productivity and about spending time wisely
                       Thank you for using Promptivity, Have a great day! 😊"""

    aggregated_str = str(compute_stats())

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
    most_common_website, most_common_reason, duration_on_site = compute_stats()

    # Call the function to create and save graphs
    bar_graph_path, pie_chart_path = generate_data()

    chat_gpt = ask_chatgpt()
    if chat_gpt is None:
        chat_gpt = genEmail(most_common_website, most_common_reason, duration_on_site)
    sendEmail(chat_gpt, email, bar_graph_path, pie_chart_path)
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


@app.route('/gettimeduration', methods=['GET'])
def get_timeduration():
    _, _, time = compute_stats()
    return jsonify({"data": format_duration(time[0][1])}), 200


def close_running_threads():
    print("awaiting running threads")
    for thread in running_threads:
        thread.join()
    print("Threads complete, ready to finish")

def generate_data():
    with app.app_context():

        querry_data_for_graphs = db.session.execute(
            text("SELECT hostname, prompt FROM sessions"))

        website_reason = querry_data_for_graphs.fetchall()

    select_query = """
        SELECT hostname, SUM(duration) AS duration
        FROM (
            SELECT hostname,
                (ROUND((JULIANDAY(r2.timestamp) - JULIANDAY(r1.timestamp)) * 86400, 2)) AS duration
            FROM sessions
                JOIN records r1
                    ON sessions.sessionID = r1.sessionID
                        AND r1.action = 'start'
                        AND r1.timestamp > DATETIME('now', '-6 days')
                JOIN records r2
                    ON sessions.sessionID = r2.sessionID
                        AND r2.action = 'end'
                        AND r2.timestamp > DATETIME('now', '-6 days')
                        AND r1.timestamp < r2.timestamp
            GROUP BY r1.timestamp, hostname
        )
        GROUP BY hostname
        ORDER BY duration DESC;
        """




    with app.app_context():
        query = db.session.execute(text(select_query))
        website_duration = query.fetchall()


    print(website_reason)
    print(website_duration)

    bar_graph_path, pie_chart_path = graph.create_and_save_graphs(website_reason, website_duration)

    #plt.show()
    return bar_graph_path, pie_chart_path




def main():
    atexit.register(close_running_threads)
    with app.app_context():
        db.create_all()
    generate_data()
    app.run(debug=True)




if __name__ == '__main__':
    main()
