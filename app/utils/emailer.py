import os.path
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying SCOPES, delete the token.json
# SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# def get_gmail_service(config=None):
#     creds = None
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             # flow = InstalledAppFlow.from_client_secrets_file('.secrets/client_secret_1035898122621-oj17gqc6qhkrtt6l3sl91q5jvnjtusu1.apps.googleusercontent.com.json', SCOPES)
#             flow = InstalledAppFlow.from_client_config(config, SCOPES)
#             creds = flow.run_local_server(port=8080)
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())

#     return build('gmail', 'v1', credentials=creds)


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
