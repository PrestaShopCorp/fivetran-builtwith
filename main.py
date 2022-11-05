import functions_framework
import functools
import requests
import os

TECHS = {
    'prestashop': 'PrestaShop',
    'magento': 'Magento',
}


class BuiltWith:
    def __init__(self, api_key):
        self._base_url = 'https://api.builtwith.com'
        self._api_key = api_key

    def list(self, tech, offset):
        params = {'KEY': self._api_key, 'TECH': tech, 'META': 'yes'}
        params = "&".join("%s=%s" % (key, value)
                          for key, value in params.items())
        if offset is not None:
            params += f'&OFFSET={offset}'

        path = os.path.join(self._base_url, 'lists11/api.json') + '?' + params
        print(f'URL: {path}')

        response = requests.get(path)
        response.raise_for_status()
        response_json = response.json()

        result = response_json.get('Results')
        offset = response_json.get('NextOffset')
        has_more = (offset != 'END')
        offset = offset if has_more else None

        return result, offset, has_more


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

    schema = {key: {'primary_key': ['D']} for key in TECHS.keys()}

    if request_json.get('setup_test'):
        return {
            'state': {},
            'schema': schema,
            'hasMore': False
        }, 200

    results = {key: builtwith.list(tech, state.get(key))
               for (key, tech) in TECHS.items()}
    insert = {key: result[0] for (key, result) in results.items()}
    state = {key: result[1] for (key, result) in results.items()}

    has_more = functools.reduce(
        lambda a, b: a or b, [result[2] for result in results.values()], False)

    return {
        'state': state,
        'schema': schema,
        'insert': insert,
        'hasMore': has_more
    }, 200
