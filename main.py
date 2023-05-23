import os
import json
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


def get_background_color(cell):
    resp = sheet.get(spreadsheetId=sheet_id, ranges=f"жидкости!{cell}", includeGridData=True).execute().get('sheets')
    color = resp[0]['data'][0]['rowData'][0]['values'][0]['effectiveFormat']['backgroundColor']
    for col in list(color):
        if col == 'red' and color[col] == 1 and len(list(color)) == 1:
            stat = False
        else: stat = True
    print(stat)


service = get_service_sacc()
sheet = service.spreadsheets()

sheet_id = "13XBmtqHjl85CtgTnbnHCqTgOdT4liOSuiPPsMk81U2U"

resp = sheet.values().get(spreadsheetId=sheet_id, range="жидкости!A4:D131").execute().get('values', [])
get_background_color('C125')
#jsonString = json.dumps(resp[0])
#pprint(jsonString[0])
liquids_name = []
liquids_taste = []
pprint(resp)

for value in resp:
    for val in value:
        if val == 'От 100р' or val == '0' or len(value) <= 1:
            resp.remove(value)

#pprint(resp)

for value in resp:
    for val in value:
        if val == 'Расценки':
            liquids_name.append(value[0])

#pprint(liquids_name)
