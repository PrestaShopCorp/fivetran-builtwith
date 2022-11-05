import functions_framework
import functools
import requests
import logging
import os

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING').upper()
logging.basicConfig(level=LOG_LEVEL)

TECHS = {
    'prestashop': 'PrestaShop'
}


class BuiltWith:
    def __init__(self, api_key):
        self._base_url = 'https://api.builtwith.com'
        self._api_key = api_key

    def _get(self, path, offset, params={}):
        params = {'KEY': self._api_key} | params
        # 'META': 'yes'
        # 'ALL': 'true'
        params = "&".join("%s=%s" % (k, v) for k, v in params.items())
        if offset is not None:
            params += f'&OFFSET={offset}'

        path = os.path.join(self._base_url, path) + '?' + params
        logging.warning(f'URL: {path}')

        response = requests.get(path)
        response.raise_for_status()
        response_json = response.json()

        results = response_json.get('Results')
        offset = response_json.get('NextOffset')
        has_more = (offset != 'END')
        offset = offset if has_more else None

        logging.warning(f'offset: {offset}')
        logging.warning(f'has_more: {has_more}')

        return results, offset, has_more

    def list(self, tech, offset):
        path = 'lists11/api.json'
        params = {'TECH': tech}
        # since = '1%20Days%20Ago'
        # params = params | {'SINCE': since}
        results, offset, has_more = self._get(path, offset, params)
        return results, offset, has_more

    def listN(self, tech, offset, n):
        pass


@functions_framework.http
def builtwith(request):
    request_json = request.get_json()
    logging.warning(f'request: {request_json}')

    state = request_json.get('state')
    if state is None:
        return 'Error: missing state value', 400

    secrets = request_json.get('secrets', {})
    api_key = secrets.get('api_key')
    if api_key is None:
        return 'Error: missing secret api_key', 400

    builtwith = BuiltWith(api_key)

    schema = {k: {'primary_key': ['D']} for (k, v) in TECHS.items()}

    if request_json.get('setup_test'):
        return {
            'state': {},
            'schema': schema,
            'hasMore': False
        }, 200

    results = {k: builtwith.list(v, state.get(k)) for (k, v) in TECHS.items()}

    insert = {k: v[0] for (k, v) in results.items()}
    state = {k: v[1] for (k, v) in results.items()}

    has_more = functools.reduce(
        lambda a, b: a or b, [v[2] for v in results.values()], False)

    return {
        'state': state,
        'schema': schema,
        'insert': insert,
        'hasMore': has_more
    }, 200
