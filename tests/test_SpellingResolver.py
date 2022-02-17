import unittest, json
import azure.functions as func
from ddt import ddt, data, unpack
from SpellingResolver.main import main

@ddt
class TestSpellingResolver(unittest.TestCase):
    @data(  (dict(query='anton marta 123', locale='de'), 'am123'),
            (dict(query='siegfried dora 2 * 7', locale='de'), 'sd77'),
            (dict(query='toni berta 22', locale='de'), 'tb22'),
            (dict(query='d e 3 times 7 2 times 3', locale='de'), 'de77733'))
    @unpack
    def test_attribute_validator(self, body, expected_output):
        # Build HTTP request
        req = func.HttpRequest(
            method  = 'GET',
            body    = json.dumps(body).encode('utf8'),
            url     = '/api/SpellingResolver',
            params  = {}
        )
        # Call the function.
        resp = main(req)

        # Check the output.
        self.assertEqual(
            resp.get_body().decode(),
            json.dumps(expected_output),
        )