import requests
import json

HOST = 'http://localhost:8080'
#HOST = 'https://europe-west1-ps-data-fivetran.cloudfunctions.net/builtwith'

FILE_PREFIX = 'data/prestashop'

data = {
    'secrets': {'api_key': 'a099b87f-906d-446f-8ead-c3e56eb61105'},
    'agent': 'Fivetran Google Cloud Functions Connector/grafted_unwound/builtwith',
}
i = 0
count = {'prestashop': 0, 'magento': 0}

state = {}
has_more = True
while has_more:
    print(f'########## {i:03} ##########')

    data.update({'state': state})
    response = requests.post(HOST, json=data)
    response_json = response.json()

    file_name = FILE_PREFIX + '_' + f'{i:05}' + '_' + str(count) + '.json'
    with open(file_name, 'w') as f:
        f.write(json.dumps(response_json, indent=4))

    state = response_json.get('state')
    tech = state.get('tech')
    print(f'tech: {tech}')
    offset = state.get('offset')
    print(f'offset: {offset}')

    has_more = response_json.get('hasMore')
    print(f'has_more: {has_more}')

    insert = response_json.get('insert')
    prestashop = insert.get('prestashop', [])
    magento = insert.get('magento', [])

    count.update({'prestashop': count.get('prestashop') + len(prestashop),
                 'magento': count.get('magento') + len(magento)})
    print(f'count: {count}')

    i += 1
