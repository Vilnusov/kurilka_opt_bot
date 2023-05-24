import os
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

CREDENTIALS_FILE = '/gs_credentials.json'
sheet_id = "13XBmtqHjl85CtgTnbnHCqTgOdT4liOSuiPPsMk81U2U"
cells = 'A4:D131'


def get_service_sacc():
    creds_json = os.path.dirname(__file__).split('\\')
    creds_json.pop()
    creds_json = '/'.join(creds_json) + CREDENTIALS_FILE

    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


service = get_service_sacc()
sheet = service.spreadsheets()


def get_background_color(cell):
    response = sheet.get(spreadsheetId=sheet_id, ranges=f"жидкости!{cell}", includeGridData=True).execute()
    response = response['sheets'][0]['data'][0]['rowData']
    status = []
    for color in response:
        color = color['values'][0]['effectiveFormat']['backgroundColor']
        col = list(color)[0]
        if col == 'red' and color[col] == 1 and len(color) == 1:
            status.append(False)
        else:
            status.append(True)
    return status


def get_liquids():
    resp = sheet.values().get(spreadsheetId=sheet_id, range=f"жидкости!{cells}").execute().get('values', [])
    liquids = []
    liquids_name_index = []

    stat = get_background_color(cells.replace('A', 'C').replace('D', 'C'))
    for i in range(len(resp)):
        if len(resp[i]) == 4:
            resp[i][2] = stat[i]

    for value in resp:
        if len(value) <= 1:
            resp.remove(value)
        for val in value:
            if val == 'От 100р' or val == '0':
                resp.remove(value)

    for i in range(len(resp)):
        for val in resp[i]:
            if val == 'Расценки':
                liquids_name_index.append(i)

    liquids_name_index.append(len(resp))

    for i in range(0, len(liquids_name_index) - 1):
        liq = []
        for j in range(liquids_name_index[i], liquids_name_index[i + 1]):
            liq.append(resp[j])
        liquids.append(liq)

    result = []
    for liq in liquids:
        t = {}
        for i in range(2, len(liq)):
            t[liq[i][1]] = liq[i][2]
        result.append([liq[0][0], liq[1][0], liq[1][3], t])

    return result
