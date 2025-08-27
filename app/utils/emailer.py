import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build



def send_email(recipient, subject, message_text, credentials=None):
    credentials = Credentials(**credentials)
    service = build("gmail", "v1", credentials=credentials)
    message = EmailMessage()
    message.set_content(message_text)
    message["To"] = recipient
    message["From"] = "me"
    message["Subject"] = subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    send_message = {"raw": encoded_message}

    return service.users().messages().send(userId="me", body=send_message).execute()
