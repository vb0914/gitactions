import requests
import json
import urllib3
import psycopg2
from datetime import datetime
urllib3.disable_warnings()

proxies = {'http': 'http://servproxy.carcgl.com:80',
'https': 'http://servproxy.carcgl.com:80'}
payload={}
url = "https://carrier.app.blackduck.com/api/tokens/authenticate"
headers = {
'Authorization': 'token YWMyMzllYzEtNzI4NC00OTQwLTk3Y2UtMmU0YTE0MzFiZmY5OjQ4ODcxZjUyLTNlOTQtNGU0OS1hODMyLTgwZWRkOTUwMTUzMg==',
'Accept': 'application/vnd.blackducksoftware.user-4+json'
}
response = requests.request("POST", url, headers=headers, data=payload, verify=False, proxies=proxies)
# print(response.text)
y = response.json()
# print(y)
token = y["bearerToken"]
# print(token)

geturl="https://carrier.app.blackduck.com/api/projects/?offset=0&limit=1000"
str ='Bearer'+' '+token
headers = {
"Authorization": str
}

result = requests.request("GET", geturl, headers=headers, data=payload, verify=False, proxies=proxies)
# print(result.data)
userlimit=json.loads(result.text)
items = userlimit['items']
final_resp =[]
count=0
for item in items[:2]:
    project_name = item['name']
    print ("project name: ",project_name)
    project_created_date = item['createdAt']
    # print ("project created date: ", project_created_date)
    datetime_obj_created = datetime.strptime(project_created_date, '%Y-%m-%dT%H:%M:%S.%fZ')
    createddate=datetime_obj_created.strftime("%d-%b-%Y")
    print(createddate)

    for link in item['_meta']['links']:
        if link['rel'] == "versions":
            get_url = link['href']
            result = requests.request("GET", get_url, headers=headers, data=payload, verify=False, proxies=proxies)
            project_detail =json.loads(result.text)
            detailed_items = project_detail['items']
            # print("detailed_items: ", detailed_items)
            for detailed_item_scan_date_check in detailed_items:
                # searching for first item having lastScanDate
                if detailed_item_scan_date_check.get('lastScanDate'):
                    max_date=detailed_item_scan_date_check.get('lastScanDate')
                    # print(max_date)
                    latest_scanned_item = detailed_item_scan_date_check
                    # print("latest_scanned_item: ", latest_scanned_item)
                    break
            else:
                # pass
                max_date = None
                latest_scanned_item = detailed_items[0]
                # print ("projects with no lastScanDate: ", detailed_items[0])
                # print("latest_scanned_item: ", latest_scanned_item)
                 
            if max_date:
                for detailed_item in detailed_items:
                    try:
                        # print ("scan details--", detailed_item['lastScanDate'], max_date) 
                        if detailed_item['lastScanDate'] > max_date:
                            max_date = detailed_item['lastScanDate']
                            latest_scanned_item = detailed_item
                            # print("scan item: ", latest_scanned_item)
                    except:
                        pass
                
                securityRiskProfile = latest_scanned_item['securityRiskProfile']
                licenseRiskProfile = latest_scanned_item['licenseRiskProfile']
                operationalRiskProfile = latest_scanned_item['operationalRiskProfile']
                version = latest_scanned_item['versionName']
                lastscandate = latest_scanned_item['lastScanDate']
                datetime_obj = datetime.strptime(lastscandate, '%Y-%m-%dT%H:%M:%S.%fZ')
                date=datetime_obj.strftime("%d-%b-%Y")
                # print ("lastest scan date", date)
                # print("version name: ",version)
                final_resp.append(
                    {
                        'name':project_name,
                        'version':version,
                        'scandate' : date,
                        'createddate': createddate,
                        'securityRiskProfile':securityRiskProfile,
                        'licenseRiskProfile':licenseRiskProfile,
                        'operationalRiskProfile': operationalRiskProfile
                    })
            # else:
            #     securityRiskProfile = latest_scanned_item['securityRiskProfile']
            #     licenseRiskProfile = latest_scanned_item['licenseRiskProfile']
            #     operationalRiskProfile = latest_scanned_item['operationalRiskProfile']
            #     version = latest_scanned_item['versionName']
            #     final_resp.append(
            #         {
            #             'name':project_name,
            #             'version':version, 
            #             'securityRiskProfile':securityRiskProfile,
            #             'licenseRiskProfile':licenseRiskProfile,
            #             'operationalRiskProfile': operationalRiskProfile
            #         })
            # break
print(final_resp)