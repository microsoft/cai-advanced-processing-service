import unittest, json
import azure.functions as func
from ddt import ddt, data, unpack
from AttributeValidator.main import main

@ddt
class TestAttributeValidator(unittest.TestCase):
    @data(({
                    "module":   "iban",
                    "region":   "de",
                    "manifest": "manifest",
                    "values": {
                        "iban": "de89370400440532013000"
                    }
                }, dict(error = False, is_valid = True, iban = "DE89370400440532013000")),
                ({
                    "module":   "iban",
                    "region":   "de",
                    "manifest": "manifest",
                    "values": {
                        "iban": "de55600800000090054000"
                    }
                }, dict(error = False, is_valid = True, iban = "DE55600800000090054000")),
                ({
                    "module":   "iban",
                    "region":   "de",
                    "manifest": "manifest",
                    "values": {
                        "iban": "de556080000009005400"
                    }
                }, dict(error = False, error_message = f"Submitted IBAN is not a valid IBAN for DE with length of 22", is_valid = False))
            )
    @unpack
    def test_attribute_validator(self, body, expected_output):
        # Set up request body.
        #body =  

        # Build HTTP request
        req = func.HttpRequest(
            method  = 'GET',
            body    = json.dumps(body).encode('utf8'),
            url     = '/api/AttributeValidator',
            params  = {}
        )
        # Call the function.
        resp = main(req)

        # Check the output.
        self.assertEqual(
            resp.get_body().decode(),
            json.dumps(expected_output),
        )