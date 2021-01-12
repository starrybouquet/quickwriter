import pickle
import os
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import re

# JSON Credentials
CREDENTIAL_FILENAME = os.getenv('GOOGLE_CREDENTIAL_FILENAME')
print(CREDENTIAL_FILENAME)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID of a sample document.
DOCUMENT_ID = '195j9eDD3ccgjQRttHhJPymLJUCOUjs-jmwTrekvdjFE'

def authorize():
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIAL_FILENAME, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    services = {}
    services['docs'] = build('docs', 'v1', credentials=creds)
    services['sheets'] = build('sheets', 'v4', credentials=creds)

    return services

def count_words(text):
    text = re.sub('/\r\n|\r|\n/g', " ", text)
    punctuationless = re.sub('/[.,\/#!$%\^&\*;:{}=\-_`~()"?“”]/g', " ", text)
    singleSpace = re.sub('/\s{2,}/g', " ", punctuationless)
    numWords = len(singleSpace.split(" "))
    return numWords

def main():
    pass

if __name__ == '__main__':
    main()