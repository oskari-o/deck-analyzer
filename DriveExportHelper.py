from __future__ import print_function

import os.path
from datetime import date
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from test_data.testSummary import test_summary_1, test_summary_2

load_dotenv()

### Very much WIP

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

# The ID of a sample document, the light memo template.
TEMPLATE_DOCUMENT_ID = os.getenv('TEMPLATE_DOCUMENT_ID')

def export_to_drive(summary: dict):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Build API services
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        # Form new document title & request body
        today = date.today()
        current_date = today.strftime("%B %d, %Y")
        company_name = summary['Light Memo'] or "Company Name"
        copy_title = f'{company_name} - Light Memo {current_date}'
        body = {
            'name': copy_title
        }

        # Copy the document and retrieve the new document ID.
        drive_response = drive_service.files().copy(
            fileId=TEMPLATE_DOCUMENT_ID, body=body).execute()
        document_copy_id = drive_response.get('id')

        # Retrieve the new documents contents from the Docs service.
        document = docs_service.documents().get(documentId=document_copy_id).execute()
        print('\n\nCreated new document, the title of the document is: {}'.format(document.get('title'))) # Can be changed to logging later

        # Form the replace requests
        replace_requests = []
        for key, value in summary.items():
            replace_requests.append({
                'replaceAllText': {
                    'containsText': {
                        'text': "{" + key + "}",
                        'matchCase': True
                    },
                    'replaceText': value
                }
            })

        # Execute the replace requests
        result = docs_service.documents().batchUpdate(
            documentId=document_copy_id, body={'requests': replace_requests}).execute()
        print("\n\nDrive Export result:\n" + str(result)) # Can be changed to logging later

        return copy_title

    except HttpError as err:
        print(err)