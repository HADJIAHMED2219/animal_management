import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import string
import random

EMAIL_ADDRESS = 'ahmed.hadji2219@gmail.com'
EMAIL_PASSWORD = 'ussi gxpf jpax baxy'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def generate_password():
    length = 10
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))
