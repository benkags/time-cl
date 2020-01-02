from __future__ import print_function
import pickle
import os
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from flask import Flask, render_template,request
app = Flask(__name__)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1MHlnUsDre6mvyXPmB65fOVdnPjvqUUubX9RXsEd3pVM'
RANGE_NAME = 'Sheet1!A2:E'

def append(sheet, data):
    w_result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            body=data,
            valueInputOption="USER_ENTERED",
            includeValuesInResponse=True).execute()
    w_values = w_result.get('updates').get('updatedData').get('values', []);
    if w_values:
        for each in w_values:
            print(each)
    else:
        print('NO data')

def get_sheet():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
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

    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    return sheet


@app.route('/', methods=['GET', 'POST'])
def ui():
    sheet = get_sheet()
    context = {}
    print(request.form)
    if request.method == 'POST':
        val = request.form.get('val')
        in_out = request.form.get('type')
        data = {
            "values": [[val, in_out, request.remote_addr]],
            "majorDimension": "ROWS"
        }
        append(sheet, data)
        context['hrs'] = val
    return render_template('index.html', **context)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

