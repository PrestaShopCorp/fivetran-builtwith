import requests

HOST = 'http://localhost:8080'

json = {'state': {},
        'secrets': {'api_key': '011ca6b0-9222-420c-9a72-7329ee3344f6'},
        'agent': 'Fivetran Google Cloud Functions Connector/grafted_unwound/builtwith',
        }

has_more = True

while has_more:
    response = requests.post(HOST, json=json)
    response_json = response.json()
    state = response_json.get('state')
    print(state)
    json.update({'state': state})
    has_more = response_json.get('hasMore')
