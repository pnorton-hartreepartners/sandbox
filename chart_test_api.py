import json
import requests
from chart_builder import dashboard_url, headers_dict, dashboard_api_test_filename

if __name__ == '__main__':
    with open(dashboard_api_test_filename) as f:
        db = json.load(f)

    # call the api
    dashboard_api_dict_json = json.dumps(db)
    rr = requests.post(dashboard_url, headers=headers_dict, data=dashboard_api_dict_json, verify=False)
    print(rr)
    print(rr.content.decode('utf-8'))
