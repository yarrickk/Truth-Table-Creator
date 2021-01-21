from __future__ import print_function

import os.path
import pickle

from gdoctableapppy import gdoctableapp
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from table_creator import TableCreator

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents']

# The ID of a sample document.
DOCUMENT_ID = '1s7kXPMBMO3CwBqv26eqprqZpPk8lk-fPH3-c66D9JNI'


def get_creds():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def main(equations, problem_number):
    creds = get_creds()
    service = build('docs', 'v1', credentials=creds)
    truth_table = TableCreator(equations=equations).create()

    table_creation_request = [{
        'insertText': {
            'endOfSegmentLocation': {'segmentId': ''},
            'text': f'\n#{problem_number}\n'
        }}, {
        'insertTable': {
            'rows': len(truth_table),
            'columns': len(truth_table[0]),
            'endOfSegmentLocation': {'segmentId': ''}
        },
    }]

    service.documents().batchUpdate(documentId=DOCUMENT_ID,
                                    body={'requests': table_creation_request}).execute()

    # data needed to work with gdoctableapp
    resource = {"oauth2": creds, "documentId": DOCUMENT_ID}
    index_of_last_table = gdoctableapp.GetTables(resource)['tables'][-1]['index']

    resource.update({
        "tableIndex": index_of_last_table,
        "values": [{
            "values": truth_table,
            "range": {"startRowIndex": 0, "startColumnIndex": 0}
        }]
    })

    # insert values of the truth_table into google doc
    gdoctableapp.SetValues(resource)


if __name__ == '__main__':
    main(["~p∧q", "p"], 12)
    main(["p∧(p∧q)"], 14)
    main(["p∨(p∧q)", "p"], 16)

    main(["p∨t", "t"], 18)
    main(["(p∧q)∧r", "p∧(q∧r)"], 21)
    main(["(p∧q)∨r", "p∧(q∨r)"], 23)

    main(["(p∧q)∨(∼p∨(p∧∼q))"], 40)
    main(["(p∧∼q)∧(∼p∨q)"], 41)
    main(["p∨∼(q∧r)", "∼q∨(p∨∼r)"], 44)
