import requests
import json

# Defining the api-endpoint
url = 'https://api.abuseipdb.com/api/v2/check'

direccion = ''
direccion = (input("Dame la direccion IP que quieres revisar: "))

querystring = {
    'ipAddress': direccion,
    'maxAgeInDays': '90'
}

headers = {
    'Accept': 'application/json',
    'Key': '28df3c1626c1908e0a104b30f79a4f256b9239d9719fd0066dfa67d662f8a75cbcd046194cde75bb'
}

response = requests.request(method='GET', url=url, headers=headers, params=querystring)

# Formatted output
decodedResponse = json.loads(response.text)
print (json.dumps(decodedResponse, sort_keys=True, indent=4))