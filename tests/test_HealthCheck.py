import unittest
import azure.functions as func
from HealthCheck.main import main

class TestHealthCheck(unittest.TestCase):
    def test_health(self):
        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method='GET',
            body=None,
            url='/api/HealthCheck',
            params={})

        # Call the function.
        resp = main(req)

        # Check the output.
        self.assertEqual(
            resp.get_body(),
            b'Healthcheck executed successfully.',
        )