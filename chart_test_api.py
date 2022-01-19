import json
import requests
from pprint import pprint as pp

url = r'https://grafana.charting.dev.mosaic.hartreepartners.com/api/dashboards/db'

headers_dict = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJrIjoiaHJ6M1B2TUQ5NmZOMFltMkN0TXZSdmlYVlNuYW9YUEkiLCJuIjoiYXBpYWNjZXNzIiwiaWQiOjF9'
}

dashboard_api_dict = {
    'dashboard': {
        'id': '24',
        #'uid': None,
        'title': 'test',
        'tags': ['no tags'],
        'timezone': 'browser',
        'schemaVersion': 16,
        'version': 0,
        'refresh': '25s',
    },
    'folderId': 1,
    'folderUid': 'Y-bj-x2nz',
    'message': 'PN changes',
    'overwrite': 'True'
}

if __name__ == '__main__':

    # use the template instead
    filename = 'chart_template.json'
    with open(filename) as f:
        db = json.load(f)

    # update the json from the docs
    dashboard_api_dict['dashboard'].update(db)

    pp(dashboard_api_dict)

    dashboard_api_dict_json = json.dumps(dashboard_api_dict)
    r1 = requests.post(url, headers=headers_dict, data=dashboard_api_dict, verify=False)
    print(r1)
    r2 = requests.post(url, headers=headers_dict, data=dashboard_api_dict_json, verify=False)
    print(r2)
    r3 = requests.post(url, headers=headers_dict, json=dashboard_api_dict_json, verify=False)
    print(r3)

    with open('chart_response1.html', 'w') as file:
        file.write(r1.content.decode('utf-8'))
