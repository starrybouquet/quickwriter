import pickle
import os
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import copy
import re
import pandas as pd

# JSON Credentials
CREDENTIAL_FILENAME = os.getenv('GOOGLE_CREDENTIAL_FILENAME')

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/spreadsheets']

# The ID of your spreadsheet tracker.
TRACKING_SHEET_ID = os.getenv('TRACKING_SHEET_ID')

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

def count_words(doc_content):
    text = read_strucutural_elements(doc_content)

    text = re.sub('/\r\n|\r|\n/g', " ", text)
    punctuationless = re.sub('/[.,\/#!$%\^&\*;:{}=\-_`~()"?“”]/g', " ", text)
    singleSpace = re.sub('/\s{2,}/g', " ", punctuationless)

    numWords = len(singleSpace.split(" "))
    return numWords

## from https://developers.google.com/docs/api/samples/extract-text#python ##

def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get('textRun')
    if not text_run:
        return ''
    return text_run.get('content')


def read_strucutural_elements(elements):
    """Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Args:
            elements: a list of Structural Elements.
    """
    text = ''
    for value in elements:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                text += read_paragraph_element(elem)
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table = value.get('table')
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                for cell in cells:
                    text += read_strucutural_elements(cell.get('content'))
        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += read_strucutural_elements(toc.get('content'))
    return text

## end google docs code ##

def access_tracking_sheet(services):

    # get spreadsheet
    result_titles = services['sheets'].spreadsheets().values().get(spreadsheetId=TRACKING_SHEET_ID, range='Sheet1!A1:A1000', majorDimension='COLUMNS').execute()
    result_ids = services['sheets'].spreadsheets().values().get(spreadsheetId=TRACKING_SHEET_ID, range='Sheet1!E1:E1000', majorDimension='COLUMNS').execute()

    results = services['sheets'].spreadsheets().values().get(spreadsheetId=TRACKING_SHEET_ID, range='Sheet1!A1:E1000', majorDimension='COLUMNS').execute()
    values = results.get('values', [])

    tracking_sheet_data = {
        'titles': values[0],
        'words': values[1],
        'ids': values[4],
        'first empty row': len(values[4])+1
    }

    return tracking_sheet_data

def track_new_document(doc_id, services, tracking_sheet_data=None):

    # count document
    doc = services['docs'].documents().get(documentId=doc_id).execute()
    content = doc.get('body').get('content')
    title = doc.get('title')
    num_words = count_words(content)

    if not tracking_sheet_data:
        tracking_sheet_data = access_tracking_sheet(services)
    
    # the sheet is of the form:
    # Title | Word Count | [blank] | Last Updated | Document ID

    row_values = [[title, num_words, '', '', doc_id]]
    row_body = {
        'values': row_values
    }

    new_row_result = services['sheets'].spreadsheets().values().update(
        spreadsheetId=TRACKING_SHEET_ID, range='A{0}:E{0}'.format(tracking_sheet_data['first empty row']), body=row_body, valueInputOption='RAW').execute()
    
    tracking_sheet_data['first empty row'] += 1
    
    return tracking_sheet_data

def update_tracker(services, update_range=[1,1000]):

    current_data = access_tracking_sheet(services)
    all_docs = services['docs'].documents()

    word_counts = current_data['words']

    all_ids = current_data['ids']
    if len(all_ids) < update_range[1]:
        update_range[1] = len(all_ids)
    
    for index in range(update_range[0], update_range[1]):
        doc_id = all_ids[index]
        doc = all_docs.get(documentId=doc_id).execute()
        content = doc.get('body').get('content')
        word_counts[index] = count_words(content)
    
    row_values = [[wordcount] for wordcount in word_counts]
    row_body = {
        'values': row_values
    }
    new_row_result = services['sheets'].spreadsheets().values().update(
        spreadsheetId=TRACKING_SHEET_ID, range='B1:B{}'.format(len(word_counts)), body=row_body, valueInputOption='RAW').execute()

def main():
    services = authorize()
    # track_new_document('DOC ID', services)
    update_tracker(services)

if __name__ == '__main__':
    main()