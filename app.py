from flask import Flask, render_template, request
import requests
import smtplib
import base64
from jira import JIRA
from flask_mail import Mail, Message

app = Flask(__name__)
# mail=Mail(app)

# Jira API configuration
BASE_URL = 'https://aryansrivastava673.atlassian.net/rest/api/3'
USERNAME = ''
API_TOKEN = ''

# SMTP server configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = ''
SMTP_PASSWORD = ''



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Fetch Jira issues assigned to the user
        issues = fetch_jira_issues()

        # Prepare email content
        email_content = render_template("email.html", issues=issues)

        # Send email
        recipient_email = request.form['email']
        send_email(recipient_email, email_content)

        return 'Email sent successfully!'

    return render_template('index.html')

def fetch_jira_issues():
    auth_str = '{}:{}'.format(USERNAME, API_TOKEN)
    auth_bytes = base64.b64encode(auth_str.encode('utf-8'))
    headers = {'Authorization': 'Basic {}'.format(auth_bytes.decode('utf-8'))}
    query = 'assignee != null AND resolution = Unresolved'
    url = BASE_URL + '/search?jql=' + query

    response = requests.get(url, headers=headers)
    data = response.json()

    issues = []
    for issue in data['issues']:
        key = issue['key']
        summary = issue['fields']['summary']
        assignee = issue['fields']['assignee']['displayName']
        url = f"https://your-jira-instance-url.com/browse/{key}"  # Replace with your Jira instance URL
        due_date = issue['fields'].get('duedate', 'N/A')
        issues.append({'key': key, 'summary': summary, 'assignee': assignee, 'url': url, 'due_date': due_date})

    return issues


def send_email(recipient_email, content):
    subject = 'Jira Issue Report'
    message = 'Subject: {}\n\n{}'.format(subject, content)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    server.sendmail(SMTP_USERNAME, recipient_email, message)
    server.quit()
    # recipient_email = request.form['recipient_email']
    # assigned_issues = fetch_jira_issues()
    #
    # msg = Message("Jira Assigned Issues", sender='your-email@example.com', recipients=[recipient_email])
    # msg.html = render_template('email.html', issues=assigned_issues, recipient_email=recipient_email)
    # mail.send(msg)


if __name__ == '__main__':
    app.run(debug=True)
