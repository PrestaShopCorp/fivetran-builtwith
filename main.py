import functions_framework
import requests
import os

TECHS = [
    {'id': 'prestashop', 'tech': 'PrestaShop'},
    {'id': 'magento', 'tech': 'Magento'},
]


class BuiltWith:
    def __init__(self, api_key):
        self._base_url = 'https://api.builtwith.com'
        self._api_key = api_key

    def list(self, tech, offset):
        params = {'KEY': self._api_key, 'TECH': tech, 'META': 'yes'}
        params = "&".join("%s=%s" % (k, v) for k, v in params.items())
        if offset is not None:
            params += f'&OFFSET={offset}'

        path = os.path.join(self._base_url, 'lists11/api.json') + '?' + params
        print(f'URL: {path}')

        response = requests.get(path)
        response.raise_for_status()
        response_json = response.json()

        data = response_json.get('Results')
        offset = response_json.get('NextOffset')
        has_more = (offset != 'END')
        offset = offset if has_more else None

        return {
            'data': data,
            'offset': offset,
            'has_more': has_more,
        }


@functions_framework.http
def builtwith(request):
    request_json = request.get_json()
    print(f'request_json: {request_json}')

    state = request_json.get('state')
    if state is None:
        return 'Error: missing state', 400

    secrets = request_json.get('secrets', {})
    api_key = secrets.get('api_key')
    if api_key is None:
        return 'Error: missing secret api_key', 400

    builtwith = BuiltWith(api_key)

    schema = {tech.get('id'): {'primary_key': ['D']} for tech in TECHS}

    if request_json.get('setup_test'):
        return {
            'state': {},
            'schema': schema,
            'hasMore': False
        }, 200

    tech = state.get('tech')
    tech = tech if tech is not None else 0

    offset = state.get('offset')

    result = builtwith.list(TECHS[tech].get('tech'), offset)

    data = result.get('data')
    offset = result.get('offset')
    has_more = result.get('has_more')

    state = {
        'tech': tech if has_more else (tech + 1) % len(TECHS),
        'offset': offset,
    }
    insert = {TECHS[tech].get('id'): data}
    has_more = has_more or (tech < len(TECHS) - 1)

    return {
        'state': state,
        'schema': schema,
        'insert': insert,
        'hasMore': has_more
    }, 200
