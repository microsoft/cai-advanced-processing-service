import unittest, json
import azure.functions as func
from ddt import ddt, data, unpack
from SpellingResolver.main import main

@ddt
class TestSpellingResolver(unittest.TestCase):
    @data( ({"query":"anton marta 123",
             "convertnumbers": True,
            "convertsymbols": True,
            "additional_symbols": {},
            "allowed_symbols": ["-" ],
             "locale":"de"
             },
            {
            "original": "anton marta 123",
            "resolved": "a m 123",
            "resolved_nospace": "am123",
            "first_letters": "a m 123",
            "first_letters_nospace": "am123"
        }),
            ({'query':'siegfried dora 2 * 7',
             "convertnumbers": True,
            "convertsymbols": True,
            "additional_symbols": {},
            "allowed_symbols": ["-" ],
             'locale':'de'
             }, 
             {
            "original": "siegfried dora 2 * 7",
            "resolved": "s d 77",
            "resolved_nospace": "sd77",
            "first_letters": "s d 77",
            "first_letters_nospace": "sd77"
        }),
            ({'query':'toni berta 22',
             "convertnumbers": True,
            "convertsymbols": True,
            "additional_symbols": {},
            "allowed_symbols": ["-" ],
             'locale':'de'
             }, 
             {
            "original": "toni berta 22",
            "resolved": "toni b 22",
            "resolved_nospace": "tonib22",
            "first_letters": "t b 22",
            "first_letters_nospace": "tb22"
        }),
            ({'query':'d e 3 times 7 2 times 3',
             "convertnumbers": True,
            "convertsymbols": True,
            "additional_symbols": {},
            "allowed_symbols": ["-" ],
             'locale':'de'
             }, 
             {
            "original": "d e 3 times 7 2 times 3",
            "resolved": "d e 777 33",
            "resolved_nospace": "de77733",
            "first_letters": "d e 777 33",
            "first_letters_nospace": "de77733"
        }))     

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