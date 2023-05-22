import os

import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

CREDENTIALS_FILE = '/gs_credentials.json'


def get_service_sacc():
    creds_json = os.path.dirname(__file__).split('\\')
    creds_json.pop()
    creds_json = '/'.join(creds_json) + CREDENTIALS_FILE

    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


service = get_service_sacc()
sheet = service.spreadsheets()

sheet_id = "13XBmtqHjl85CtgTnbnHCqTgOdT4liOSuiPPsMk81U2U"

resp = sheet.values().get(spreadsheetId=sheet_id, range="жидкости!A4:D147").execute().get('values', [])
pprint(resp)
liquids = []

for value in resp:
    for val in value:
        if val == 'От 100р' or val == '0' or len(value) == 1:
            resp.remove(value)

pprint(resp)

for value in resp:
    for val in value:
        if val == 'Расценки':
            liquids.append(value[0])

pprint(liquids)
