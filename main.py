import functions_framework
import functools
import requests
import os

TECHS = ['PrestaShop']


class BuiltWith:
    def __init__(self, api_key):
        self._base_url = 'https://api.builtwith.com'
        self._api_key = api_key

    def _get(self, path, state, params={}):
        params = params | {'KEY': self._api_key, 'META': 'yes', 'ALL': 'true'}

        if state is not None:
            params = params | {'OFFSET': state}

        path = os.path.join(self._base_url, path)
        response = requests.get(path, params=params)
        response.raise_for_status()
        response_json = response.json()

        results = response_json.get('Results')
        offset = response_json.get('NextOffset')
        has_more = offset is None

        return response_json, offset, has_more

    def list(self, tech, state):
        path = 'lists10/api.json'
        params = {'TECH': tech}
        results, state, has_more = self._get(path, state, params)
        print(f'{tech}: {state}')
        return results, state, has_more


@functions_framework.http
def builtwith(request):
    request_json = request.get_json()
    print(f'request: ${request_json}')

    state = request_json.get('state')
    if state is None:
        return 'Error: missing state value', 400

    secrets = request_json.get('secrets', {})
    api_key = secrets.get('api_key')
    if api_key is None:
        return 'Error: missing secret api_key', 400

    builtwith = BuiltWith(api_key)

    schema = {
        'prestashop': {
            'primary_key': ['D']
        }
    }

    if request_json.get('setup_test'):
        return {
            'state': {},
            'schema': schema,
            'hasMore': False
        }, 200

    results = {builtwith.list(tech, state.get(tech)) for tech in TECHS}

    insert = {k: v[0] for (k, v) in results.iteritems()}
    state = {k: v[1] for (k, v) in results.iteritems()}

    has_more = functools.reduce(
        lambda a, b: a or b, {k: v[1] for (k, v) in results.iteritems()})

    return {
        'state': state,
        'schema': schema,
        'insert': insert,
        'hasMore': has_more
    }, 200
