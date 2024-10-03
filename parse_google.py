import httplib2 
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials	

CREDENTIALS_FILE = 'silader-dairy-dbd97bd99be0.json'  

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http()) 
service = googleapiclient.discovery.build('sheets', 'v4', http = httpAuth)

def get_data_from_google_sheet(sheet, feild, sheetid):
  try:
    ranges = [f"{sheet}!{feild}"]   
    results = service.spreadsheets().values().batchGet(spreadsheetId = sheetid, 
                                        ranges = ranges, 
                                        valueRenderOption = 'FORMATTED_VALUE',  
                                        dateTimeRenderOption = 'FORMATTED_STRING').execute() 
    sheet_values = results['valueRanges'][0]
    if len(sheet_values.keys()) == 2:
      return []
    ans = sheet_values['values']
    for i in range(len(ans)):
      ans[i] = ' '.join(ans[i])
    print(ans)
    return ans
  except:
    return False
#print(get_data_from_google_sheet('5 класс', 'A3', '1GfRGWH9PzMkfqhCmgNSN2ejj7ih-W97caYd9QPSgM9c'))